from __future__ import annotations

import importlib
from pathlib import Path

import pytest

pytest.importorskip("flask")


def _load_app(monkeypatch, tmp_path):
    data = tmp_path / "data"
    ancient = data / "易經古原文暫存戰果資料夾"
    yijing_input = data / "易經輸入端資料夾"
    ancient.mkdir(parents=True)
    yijing_input.mkdir(parents=True)

    monkeypatch.setenv("DAD_PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("DAD_CONFIG_DATA_DIR", str(data))
    monkeypatch.setenv("DAD_SECRET_KEY", "test-secret")
    monkeypatch.setenv("DAD_AUTO_INITIALIZE", "0")

    import src.config as config
    importlib.reload(config)
    import src.data_processor as data_processor
    import src.wiki_handler as wiki_handler
    import src.slide_generator as slide_generator
    import src.page_generator as page_generator
    import src.main as main
    for module in (data_processor, wiki_handler, slide_generator, page_generator, main):
        importlib.reload(module)

    app = main.create_app({"TESTING": True})
    return app


def test_index_renders_and_contains_csrf_token(monkeypatch, tmp_path):
    app = _load_app(monkeypatch, tmp_path)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b'name="_csrf_token"' in response.data


def test_post_without_csrf_token_is_rejected(monkeypatch, tmp_path):
    app = _load_app(monkeypatch, tmp_path)
    response = app.test_client().post("/process_interaction", data={})
    assert response.status_code == 400


def test_safe_defaults_do_not_initialize_or_enable_debug(monkeypatch, tmp_path):
    app = _load_app(monkeypatch, tmp_path)
    assert app.secret_key == b"test-secret" or app.secret_key == "test-secret"
    assert app.debug is False
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

def test_valid_form_submission_uses_flash_message(monkeypatch, tmp_path):
    import re

    app = _load_app(monkeypatch, tmp_path)
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


def test_file_content_is_html_escaped(monkeypatch, tmp_path):
    app = _load_app(monkeypatch, tmp_path)
    data = tmp_path / "data"
    ancient = data / "易經古原文暫存戰果資料夾"
    yijing_input = data / "易經輸入端資料夾"
    (ancient / "yijing標題.txt").write_text("乾<script>\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text(
        "<script>alert(1)</script>\n", encoding="utf-8"
    )
    (yijing_input / "測試.txt").write_text("<script>alert(2)</script>", encoding="utf-8")
    client = app.test_client()

    gua_response = client.get("/gua/1")
    case_response = client.get("/fengshui/case/測試")

    assert "<script>alert(1)</script>" not in gua_response.get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in gua_response.get_data(as_text=True)
    assert "<script>alert(2)</script>" not in case_response.get_data(as_text=True)
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in case_response.get_data(as_text=True)


def test_tuanxiang_route_has_a_real_template(monkeypatch, tmp_path):
    app = _load_app(monkeypatch, tmp_path)
    response = app.test_client().get("/slides/lecture_tuanxiang")
    assert response.status_code == 200
