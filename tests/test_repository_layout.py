from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "python" / "src"
TEMPLATES = SRC / "templates"


def test_catalog_grid_keeps_two_columns_at_narrow_viewports():
    stylesheet = (SRC / "static" / "style.css").read_text(encoding="utf-8")
    column_rules = re.findall(
        r"\.catalog-grid(?:\s*,\s*\.catalog-grid--slides)?\s*\{[^}]*"
        r"grid-template-columns:\s*([^;]+);",
        stylesheet,
        flags=re.DOTALL,
    )

    assert column_rules[-1].strip() == "repeat(2, minmax(0, 1fr))"


def test_every_rendered_template_exists():
    required = {
        "base.html",
        "error.html",
        "index.html",
        "gua_page.html",
        "fengshui_case_page.html",
        "impress_slides_base.html",
        "slides_yijing_lecture.html",
        "slides_yijing_guaci_moms_records.html",
        "slides_yijing_tuanxiang.html",
        "workspace.html",
    }
    assert required <= {path.name for path in TEMPLATES.glob("*.html")}


def test_slide_base_has_accessible_controls_and_external_assets():
    content = (TEMPLATES / "impress_slides_base.html").read_text(encoding="utf-8")

    assert "data-slide-prev" in content
    assert "data-slide-next" in content
    assert "data-slide-progress" in content
    assert "data-slide-help-toggle" in content
    assert "filename='slides-controls.css'" in content
    assert "filename='slides-controls.js'" in content
    assert "impress().init()" not in content


def test_slide_controls_restore_pointer_events_outside_impress():
    stylesheet = (SRC / "static" / "slides-controls.css").read_text(encoding="utf-8")

    assert ".impress-enabled .slide-toolbar" in stylesheet
    assert ".impress-enabled .slide-help" in stylesheet
    assert "pointer-events: auto" in stylesheet
    assert re.search(
        r"\[data-slide-help\]\[hidden\]\s*\{[^}]*display:\s*none",
        stylesheet,
        flags=re.DOTALL,
    )


def test_slide_help_distinguishes_focus_and_deck_navigation_shortcuts():
    content = (TEMPLATES / "impress_slides_base.html").read_text(encoding="utf-8")

    assert "Tab / Shift+Tab 在上方控制項之間移動" in content
    assert "焦點不在控制項時，可使用方向鍵、空白鍵或 Page Up / Page Down 切換投影片" in content
    assert "Page Up / Page Down 或 Tab" not in content
    assert "按 Esc 查看全覽" not in content


def test_slide_controller_guards_native_control_keys_before_deck_init():
    controller = (SRC / "static" / "slides-controls.js").read_text(encoding="utf-8")
    init_position = controller.index("deck.init()")

    assert controller.index('document.addEventListener("keydown"') < init_position
    assert controller.index('document.addEventListener("keyup"') < init_position
    assert 'event.key === "Tab"' in controller
    assert '.closest(".slide-toolbar, [data-slide-help]")' in controller
    assert "event.stopImmediatePropagation()" in controller
    for key in (" ", "ArrowLeft", "ArrowUp", "ArrowRight", "ArrowDown", "PageUp", "PageDown"):
        assert f'"{key}"' in controller


def test_page_frames_declare_a_self_contained_favicon():
    for template_name in ("base.html", "impress_slides_base.html"):
        content = (TEMPLATES / template_name).read_text(encoding="utf-8")

        assert 'rel="icon" href="data:,"' in content


def test_reading_templates_use_shared_base_without_inline_styles():
    for template_name in {"gua_page.html", "fengshui_case_page.html"}:
        content = (TEMPLATES / template_name).read_text(encoding="utf-8")

        assert '{% extends "base.html" %}' in content
        assert "<style>" not in content


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
    assert "<form" not in content
    assert "action=" not in content


def test_workspace_uses_dedicated_assets_without_generate_all_shortcut():
    content = (TEMPLATES / "workspace.html").read_text(encoding="utf-8")

    assert (SRC / "static" / "workspace.js").is_file()
    assert "filename='workspace.js'" in content
    assert content.count("data-operation") == 7
    assert "generate_all_outputs" not in content


def test_main_has_no_hardcoded_secret_or_always_on_debugger():
    content = (SRC / "main.py").read_text(encoding="utf-8")
    assert "your_very_secret_key" not in content
    assert "debug=True" not in content
    assert "build_content_catalog" in content
    assert "initialize_all_data" not in content
    assert "process_interaction" not in content
    assert "DAD_AUTO_INITIALIZE" in content


def test_docs_describe_reading_home_workspace_and_slide_controls():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "http://127.0.0.1:5003/" in readme
    assert "/workspace" in readme
    assert "標題搜尋" in readme
    assert "投影片控制" in readme
    assert "Tab / Shift+Tab 在控制項間移動" in readme
    assert "Page Up / Page Down 或 Tab 移動" not in readme


def test_visual_companion_artifacts_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".superpowers/" in ignore
