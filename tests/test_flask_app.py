from __future__ import annotations

import pytest

pytest.importorskip("flask")

def test_index_renders_and_contains_csrf_token(app_factory):
    app, _ = app_factory()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b'name="_csrf_token"' in response.data


def test_post_without_csrf_token_is_rejected(app_factory):
    app, _ = app_factory()
    response = app.test_client().post("/process_interaction", data={})
    assert response.status_code == 400


def test_safe_defaults_do_not_initialize_or_enable_debug(app_factory):
    app, _ = app_factory()
    assert app.secret_key == b"test-secret" or app.secret_key == "test-secret"
    assert app.debug is False
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

def test_valid_form_submission_uses_flash_message(app_factory):
    import re

    app, _ = app_factory()
    client = app.test_client()
    page = client.get("/")
    token_match = re.search(rb'name="_csrf_token" value="([^"]+)"', page.data)
    assert token_match is not None

    response = client.post(
        "/process_interaction",
        data={
            "_csrf_token": token_match.group(1).decode("utf-8"),
            "custom_topic_start": "1",
            "custom_topic_end": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "未選擇任何操作" in response.get_data(as_text=True)


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


def test_tuanxiang_route_has_a_real_template(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/slides/lecture_tuanxiang")
    assert response.status_code == 200


def _seed_two_guas(data):
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text("乾\n坤\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text("乾：元亨利貞。\n", encoding="utf-8")
    (ancient / "yijing切開第2卦古原文無分斷點.txt").write_text("坤：元亨。\n", encoding="utf-8")


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
