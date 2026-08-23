from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "python" / "src"
TEMPLATES = SRC / "templates"


def test_every_rendered_template_exists():
    required = {
        "index.html",
        "gua_page.html",
        "fengshui_case_page.html",
        "impress_slides_base.html",
        "slides_yijing_lecture.html",
        "slides_yijing_guaci_moms_records.html",
        "slides_yijing_tuanxiang.html",
    }
    assert required <= {path.name for path in TEMPLATES.glob("*.html")}


def test_templates_do_not_disable_autoescaping_for_file_content():
    unsafe = []
    for path in TEMPLATES.glob("*.html"):
        if "| safe" in path.read_text(encoding="utf-8") or "|safe" in path.read_text(encoding="utf-8"):
            unsafe.append(path.name)
    assert unsafe == []


def test_index_uses_catalog_assets_and_has_no_processing_form():
    content = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    assert "data-catalog-search" in content
    assert "data-catalog-entry" in content
    assert "filename='catalog.js'" in content
    assert "process_interaction" not in content
    assert 'name="_csrf_token"' not in content


def test_main_has_no_hardcoded_secret_or_always_on_debugger():
    content = (SRC / "main.py").read_text(encoding="utf-8")
    assert "your_very_secret_key" not in content
    assert "debug=True" not in content
    assert "build_content_catalog" in content
    assert "get_flashed_messages" not in content
    assert "DAD_AUTO_INITIALIZE" in content
