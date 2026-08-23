from __future__ import annotations

from pathlib import Path

import pytest

from src.file_utils import upsert_text_section


def test_upsert_text_section_is_idempotent_and_preserves_other_content(tmp_path):
    output = tmp_path / "book.txt"
    output.write_text("手動前言\n", encoding="utf-8")

    upsert_text_section(output, "ancient", "第一版")
    upsert_text_section(output, "ancient", "第二版")

    content = output.read_text(encoding="utf-8")
    assert content.startswith("手動前言")
    assert content.count("[[DAD:ancient:BEGIN]]") == 1
    assert content.count("[[DAD:ancient:END]]") == 1
    assert "第一版" not in content
    assert content.count("第二版") == 1


def test_upsert_text_section_creates_parent_and_initial_header(tmp_path):
    output = tmp_path / "nested" / "book.txt"
    upsert_text_section(output, "wiki", "內容", initial_header="我的著作")
    content = output.read_text(encoding="utf-8")
    assert content.startswith("我的著作")
    assert "內容" in content


def test_upsert_text_section_refuses_incomplete_markers(tmp_path):
    output = tmp_path / "book.txt"
    output.write_text("[[DAD:broken:BEGIN]]\n殘缺", encoding="utf-8")
    with pytest.raises(ValueError):
        upsert_text_section(output, "broken", "new")
