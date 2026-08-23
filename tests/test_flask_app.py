from __future__ import annotations

import pytest

pytest.importorskip("flask")


def _csrf_from(html: bytes) -> str:
    import re

    match = re.search(rb'name="_csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1).decode("utf-8")


def test_index_renders_shared_navigation(app_factory):
    app, _ = app_factory()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<html lang="zh-Hant">' in html
    assert 'class="skip-link" href="#main-content"' in html
    assert 'nav aria-label="主要導覽"' in html


def test_workspace_requires_csrf_and_old_route_is_removed(app_factory):
    app, _ = app_factory()
    client = app.test_client()
    assert client.post("/workspace/process", data={}).status_code == 400
    assert client.post("/process_interaction", data={}).status_code == 404


def test_safe_defaults_do_not_initialize_or_enable_debug(app_factory):
    app, _ = app_factory()
    assert app.secret_key == b"test-secret" or app.secret_key == "test-secret"
    assert app.debug is False
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

def test_workspace_empty_submission_redirects_to_structured_warning(app_factory):
    app, _ = app_factory()
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={"_csrf_token": token, "custom_topic_start": "1", "custom_topic_end": "1"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workspace")
    html = client.get("/workspace").get_data(as_text=True)
    assert "未選擇任何操作" in html
    assert 'data-result-status="warning"' in html


def test_workspace_selected_operation_uses_prg_and_renders_success(
    app_factory, monkeypatch
):
    app, _ = app_factory()
    import src.main as main

    selections = []

    def fake_run(selection):
        selections.append(selection)
        return (
            main.ProcessingStepResult(
                "環境準備", "success", "環境準備完成，既有檔案已保留。"
            ),
        )

    monkeypatch.setattr(main, "run_processing", fake_run)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_prepare_environment": "true",
            "custom_topic_start": "1",
            "custom_topic_end": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert selections[0].run_prepare_env is True
    html = response.get_data(as_text=True)
    assert "環境準備完成" in html
    assert 'data-result-status="success"' in html


def test_workspace_invalid_range_is_reported_without_running(app_factory, monkeypatch):
    app, _ = app_factory()
    import src.main as main

    def fail_if_called(_selection):
        raise AssertionError("run_processing must not be called for an invalid range")

    monkeypatch.setattr(main, "run_processing", fail_if_called)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_process_custom_wiki": "true",
            "custom_topic_start": "10",
            "custom_topic_end": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "輸入資料有誤" in response.get_data(as_text=True)
    assert 'data-result-status="error"' in response.get_data(as_text=True)


@pytest.mark.parametrize(
    ("start", "end"),
    [(1, 1), (10_000, 10_000), (1, 50), (9_951, 10_000)],
)
def test_workspace_accepts_range_limits_and_inclusive_span_of_50(
    app_factory, monkeypatch, start, end
):
    app, _ = app_factory()
    import src.main as main

    selections = []

    def fake_run(selection):
        selections.append(selection)
        return (main.ProcessingStepResult("範圍", "success", "範圍有效。"),)

    monkeypatch.setattr(main, "run_processing", fake_run)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_process_custom_wiki": "true",
            "custom_topic_start": str(start),
            "custom_topic_end": str(end),
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workspace")
    assert len(selections) == 1
    assert (
        selections[0].custom_topic_start,
        selections[0].custom_topic_end,
    ) == (start, end)


@pytest.mark.parametrize(
    ("start", "end"),
    [(0, 1), (1, 10_001), (1, 51)],
)
def test_workspace_rejects_range_outside_limits_or_over_inclusive_span_50(
    app_factory, monkeypatch, start, end
):
    app, _ = app_factory()
    import src.main as main

    def fail_if_called(_selection):
        raise AssertionError("run_processing must not be called for an invalid range")

    monkeypatch.setattr(main, "run_processing", fail_if_called)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_process_custom_wiki": "true",
            "custom_topic_start": str(start),
            "custom_topic_end": str(end),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "輸入資料有誤" in html
    assert 'data-result-status="error"' in html


def test_file_content_is_html_escaped(app_factory):
    app, data = app_factory()
    ancient = data / "易經古原文暫存戰果資料夾"
    yijing_input = data / "易經輸入端資料夾"
    (ancient / "yijing標題.txt").write_text("乾<script>\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text(
        "<script>alert(1)</script>\n", encoding="utf-8"
    )
    (yijing_input / "易經個案列表.txt").write_text("測試\n", encoding="utf-8")
    (yijing_input / "測試.txt").write_text("<script>alert(2)</script>", encoding="utf-8")
    client = app.test_client()

    gua_response = client.get("/gua/1")
    case_response = client.get("/fengshui/case/測試")

    assert "<script>alert(1)</script>" not in gua_response.get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in gua_response.get_data(as_text=True)
    assert "<script>alert(2)</script>" not in case_response.get_data(as_text=True)
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in case_response.get_data(as_text=True)


def test_gua_page_has_sections_and_next_navigation(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    html = app.test_client().get("/gua/1").get_data(as_text=True)

    assert 'id="ancient-text"' in html
    assert 'id="wiki-reference"' in html
    assert 'id="external-links"' in html
    assert 'href="/gua/2"' in html
    assert "下一卦：坤" in html
    assert "1 / 2" in html


def test_missing_content_uses_friendly_404_template(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/fengshui/case/不存在")

    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "找不到內容" in html
    assert 'href="/"' in html


def test_tuanxiang_route_has_a_real_template(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/slides/lecture_tuanxiang")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "data-slide-progress" in html
    assert "返回首頁" in html
    assert "slides-controls.js" in html


def _seed_two_guas(data):
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text("乾\n坤\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text("乾：元亨利貞。\n", encoding="utf-8")
    (ancient / "yijing切開第2卦古原文無分斷點.txt").write_text("坤：元亨。\n", encoding="utf-8")


def test_index_renders_catalog_counts_and_unavailable_cases(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    inputs = data / "易經輸入端資料夾"
    (inputs / "易經個案列表.txt").write_text("易經個案001\n易經個案002\n", encoding="utf-8")
    (inputs / "易經個案001.txt").write_text("內容\n", encoding="utf-8")

    html = app.test_client().get("/").get_data(as_text=True)

    assert "2" in html
    assert "3" in html
    assert "1 / 2" in html
    assert 'data-kind="gua"' in html
    assert 'data-search="第 1 卦 1 乾 六十四卦 gua"' in html
    assert "易經個案002" in html
    assert "缺少內容檔" in html
    missing_card = html.split("易經個案002", 1)[1].split("</article>", 1)[0]
    assert "href=" not in missing_card


def test_index_survives_missing_titles_with_workspace_recovery(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "尚未找到卦名資料" in html
    assert 'href="/workspace"' in html


def test_index_renders_without_a_processing_form(app_factory):
    app, _ = app_factory()
    html = app.test_client().get("/").get_data(as_text=True)
    assert 'data-catalog-search' in html
    assert 'name="_csrf_token"' not in html
    assert '/process_interaction' not in html


def test_workspace_shell_is_reachable(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/workspace")
    assert response.status_code == 200
    assert "資料工作台" in response.get_data(as_text=True)


def test_gua_route_returns_404_outside_catalog(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    client = app.test_client()

    assert client.get("/gua/1").status_code == 200
    assert client.get("/gua/3").status_code == 404
    assert client.get("/gua/65").status_code == 404


def test_all_64_catalog_gua_routes_are_readable(app_factory):
    app, data = app_factory()
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text(
        "\n".join(f"卦名{number:02d}" for number in range(1, 65)) + "\n",
        encoding="utf-8",
    )
    client = app.test_client()

    assert [client.get(f"/gua/{number}").status_code for number in range(1, 65)] == [
        200
    ] * 64


def test_gua_route_rejects_65_even_when_catalog_has_65_titles(app_factory):
    app, data = app_factory()
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text(
        "\n".join(f"卦名{number:02d}" for number in range(1, 66)) + "\n",
        encoding="utf-8",
    )

    assert app.test_client().get("/gua/65").status_code == 404


def test_fengshui_route_reads_input_directory_and_missing_is_404(app_factory):
    app, data = app_factory()
    inputs = data / "易經輸入端資料夾"
    (inputs / "易經個案列表.txt").write_text("易經個案001\n易經個案002\n", encoding="utf-8")
    (inputs / "易經個案001.txt").write_text("可閱讀內容\n", encoding="utf-8")
    client = app.test_client()

    available = client.get("/fengshui/case/易經個案001")
    missing = client.get("/fengshui/case/易經個案002")
    unknown = client.get("/fengshui/case/不存在")

    assert available.status_code == 200
    assert "可閱讀內容" in available.get_data(as_text=True)
    assert missing.status_code == 404
    assert unknown.status_code == 404
