from __future__ import annotations

from pathlib import Path

import pytest

from src.app_support import env_flag, resolve_existing_child, text_to_html, validate_range


def test_env_flag_understands_common_boolean_values(monkeypatch):
    monkeypatch.setenv("FEATURE", "yes")
    assert env_flag("FEATURE") is True
    monkeypatch.setenv("FEATURE", "0")
    assert env_flag("FEATURE", default=True) is False
    monkeypatch.setenv("FEATURE", "unexpected")
    assert env_flag("FEATURE", default=True) is True


def test_validate_range_rejects_invalid_or_excessive_ranges():
    assert validate_range(2, 5, minimum=1, maximum=64, max_span=10) == (2, 5)
    with pytest.raises(ValueError):
        validate_range(0, 5, minimum=1, maximum=64)
    with pytest.raises(ValueError):
        validate_range(10, 5, minimum=1, maximum=64)
    with pytest.raises(ValueError):
        validate_range(1, 20, minimum=1, maximum=64, max_span=10)


def test_resolve_existing_child_blocks_path_traversal(tmp_path):
    base = tmp_path / "cases"
    base.mkdir()
    case = base / "安全個案.txt"
    case.write_text("ok", encoding="utf-8")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    assert resolve_existing_child(base, "安全個案", suffixes=(".txt",)) == case.resolve()
    with pytest.raises(ValueError):
        resolve_existing_child(base, "../secret", suffixes=(".txt",))


def test_text_to_html_escapes_file_content_and_preserves_lines():
    rendered = str(text_to_html("<script>alert(1)</script>\nA&B"))
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "A&amp;B" in rendered
    assert "<br>" in rendered
