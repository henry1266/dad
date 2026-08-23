from __future__ import annotations

from pathlib import Path

import src.data_processor as dp


def _configure_paths(monkeypatch, tmp_path):
    source = tmp_path / "source"
    data = tmp_path / "data"
    source.mkdir()
    data.mkdir()

    mapping = {
        "BASH_SOURCE_DIR": source,
        "CONFIG_DATA_PATH": data,
        "BASIC_DATA_PATH": data / "基本資料資料夾",
        "YIJING_INPUT_PATH": data / "易經輸入端資料夾",
        "TOOL_DATA_PATH": data / "工具程式資料夾",
        "HTML_TEMPLATE_PATH": data / "HTML參考樣板資料夾",
        "SLIDES_TEMPLATE_PATH": data / "投影片參考樣板資料夾",
        "FENGSHUI_CASES_PATH": data / "易經個案資料夾",
        "M_TXT_PATH": data / "m.txt",
        "YIJING_TOTAL_RESULT_PATH": data / "總戰果",
        "YIJING_RESULT_PATH": data / "戰果",
        "YIJING_INTERMEDIATE_PATH": data / "中間",
        "YIJING_MARKING_PATH": data / "標記",
        "YIJING_WIKI_RESULT_PATH": data / "維基結果",
        "YIJING_ANCIENT_TEXT_PATH": data / "古文結果",
        "YIJING_HTML_RESULT_PATH": data / "HTML結果",
        "YIJING_SLIDES_RESULT_PATH": data / "投影片結果",
        "YIJING_WIKI_TEMP_PATH": data / "維基暫存",
        "YIJING_ANCIENT_TEMP_PATH": data / "古文暫存",
        "YIJING_HTML_TEMP_PATH": data / "HTML暫存",
        "YIJING_SLIDES_TEMP_PATH": data / "投影片暫存",
        "YIJING_WIKI_GUA_RAW_PATH": data / "維基暫存" / "1",
        "YIJING_WIKI_GUA_CLEANED_PATH": data / "維基暫存" / "5",
        "MAIN_COMPILATION_FILE": data / "總戰果" / "我的著作文獻部份.txt",
    }
    for name, value in mapping.items():
        monkeypatch.setattr(dp, name, str(value))
    return source, data


def test_prepare_environment_preserves_existing_files_by_default(monkeypatch, tmp_path):
    source, data = _configure_paths(monkeypatch, tmp_path)
    source_basic = source / "基本資料資料夾"
    source_basic.mkdir()
    (source_basic / "new.txt").write_text("new", encoding="utf-8")
    (source_basic / "same.txt").write_text("source", encoding="utf-8")

    dest_basic = data / "基本資料資料夾"
    dest_basic.mkdir()
    (dest_basic / "same.txt").write_text("user-edited", encoding="utf-8")
    (dest_basic / "only-local.txt").write_text("keep", encoding="utf-8")

    dp.prepare_environment()

    assert (dest_basic / "same.txt").read_text(encoding="utf-8") == "user-edited"
    assert (dest_basic / "only-local.txt").read_text(encoding="utf-8") == "keep"
    assert (dest_basic / "new.txt").read_text(encoding="utf-8") == "new"


def test_prepare_environment_reset_replaces_managed_directories(monkeypatch, tmp_path):
    source, data = _configure_paths(monkeypatch, tmp_path)
    source_basic = source / "基本資料資料夾"
    source_basic.mkdir()
    (source_basic / "same.txt").write_text("source", encoding="utf-8")

    dest_basic = data / "基本資料資料夾"
    dest_basic.mkdir()
    (dest_basic / "same.txt").write_text("user-edited", encoding="utf-8")
    (dest_basic / "only-local.txt").write_text("remove", encoding="utf-8")

    dp.prepare_environment(reset=True)

    assert (dest_basic / "same.txt").read_text(encoding="utf-8") == "source"
    assert not (dest_basic / "only-local.txt").exists()

def test_append_ancient_texts_replaces_generated_section(monkeypatch, tmp_path):
    ancient = tmp_path / "ancient"
    ancient.mkdir()
    (ancient / "yijing標題.txt").write_text("乾\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text(
        "《易經》第一卦 乾\n乾：元亨利貞。\n", encoding="utf-8"
    )
    compilation = tmp_path / "book.txt"
    compilation.write_text("手動內容\n", encoding="utf-8")
    monkeypatch.setattr(dp, "YIJING_ANCIENT_TEXT_PATH", str(ancient))
    monkeypatch.setattr(dp, "MAIN_COMPILATION_FILE", str(compilation))

    dp.append_ancient_texts_to_compilation()
    dp.append_ancient_texts_to_compilation()

    content = compilation.read_text(encoding="utf-8")
    assert content.startswith("手動內容")
    assert content.count("[[DAD:ancient_texts:BEGIN]]") == 1
    assert content.count("乾：元亨利貞。") == 1
