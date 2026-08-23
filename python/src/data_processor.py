# -*- coding: utf-8 -*-
"""Filesystem and source-text processing for the DAD application."""
from __future__ import annotations

import glob
import os
import re
import shutil
import traceback
from pathlib import Path

from .file_utils import upsert_text_section

from .config import (
    BASH_SOURCE_DIR,
    BASIC_DATA_PATH,
    CONFIG_DATA_PATH,
    FENGSHUI_CASES_PATH,
    HTML_TEMPLATE_PATH,
    MAIN_COMPILATION_FILE,
    M_TXT_PATH,
    SLIDES_TEMPLATE_PATH,
    TOOL_DATA_PATH,
    YIJING_ANCIENT_TEMP_PATH,
    YIJING_ANCIENT_TEXT_PATH,
    YIJING_HTML_RESULT_PATH,
    YIJING_HTML_TEMP_PATH,
    YIJING_INPUT_PATH,
    YIJING_INTERMEDIATE_PATH,
    YIJING_MARKING_PATH,
    YIJING_RESULT_PATH,
    YIJING_SLIDES_RESULT_PATH,
    YIJING_SLIDES_TEMP_PATH,
    YIJING_TOTAL_RESULT_PATH,
    YIJING_WIKI_GUA_CLEANED_PATH,
    YIJING_WIKI_GUA_RAW_PATH,
    YIJING_WIKI_RESULT_PATH,
    YIJING_WIKI_TEMP_PATH,
)


def _copy_missing_tree(source: str, destination: str) -> None:
    """Copy missing files without overwriting user-edited destination files."""
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    for item in source_path.rglob("*"):
        relative = item.relative_to(source_path)
        target = destination_path / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def prepare_environment(reset: bool = False) -> None:
    """Create the runtime structure and copy seed data safely.

    The default mode is non-destructive: existing files are retained and only
    missing seed files are copied. ``reset=True`` is intentionally explicit and
    replaces the managed seed directories with the source copies.
    """
    print("Preparing environment...")
    os.makedirs(CONFIG_DATA_PATH, exist_ok=True)
    dirs_to_copy = {
        "基本資料資料夾": BASIC_DATA_PATH,
        "易經輸入端資料夾": YIJING_INPUT_PATH,
        "工具程式資料夾": TOOL_DATA_PATH,
        "HTML參考樣板資料夾": HTML_TEMPLATE_PATH,
        "投影片參考樣板資料夾": SLIDES_TEMPLATE_PATH,
        "易經個案資料夾": FENGSHUI_CASES_PATH,
    }

    for src_dirname, dest_path in dirs_to_copy.items():
        src_path = os.path.join(BASH_SOURCE_DIR, src_dirname)
        if reset and os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        if os.path.isdir(src_path):
            if reset:
                shutil.copytree(src_path, dest_path)
            else:
                _copy_missing_tree(src_path, dest_path)
            print(f"Synced {src_path} to {dest_path}")
        else:
            print(f"Warning: Source directory {src_path} not found.")
            os.makedirs(dest_path, exist_ok=True)

    m_txt_src = os.path.join(BASH_SOURCE_DIR, "m.txt")
    if os.path.isfile(m_txt_src) and (reset or not os.path.exists(M_TXT_PATH)):
        os.makedirs(os.path.dirname(M_TXT_PATH), exist_ok=True)
        shutil.copy2(m_txt_src, M_TXT_PATH)
        print(f"Copied {m_txt_src} to {M_TXT_PATH}")
    elif not os.path.isfile(m_txt_src):
        print(f"Warning: Source file {m_txt_src} not found.")

    dirs_to_create = [
        YIJING_TOTAL_RESULT_PATH,
        YIJING_RESULT_PATH,
        YIJING_INTERMEDIATE_PATH,
        YIJING_MARKING_PATH,
        YIJING_WIKI_RESULT_PATH,
        YIJING_ANCIENT_TEXT_PATH,
        YIJING_HTML_RESULT_PATH,
        YIJING_SLIDES_RESULT_PATH,
        YIJING_WIKI_TEMP_PATH,
        YIJING_ANCIENT_TEMP_PATH,
        YIJING_HTML_TEMP_PATH,
        YIJING_SLIDES_TEMP_PATH,
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果1資料夾"),
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果2資料夾"),
        YIJING_WIKI_GUA_RAW_PATH,
        YIJING_WIKI_GUA_CLEANED_PATH,
    ]
    for path_to_create in dirs_to_create:
        os.makedirs(path_to_create, exist_ok=True)
    for index in range(1, 7):
        os.makedirs(os.path.join(YIJING_WIKI_TEMP_PATH, str(index)), exist_ok=True)

    if not os.path.exists(MAIN_COMPILATION_FILE) or os.path.getsize(MAIN_COMPILATION_FILE) == 0:
        os.makedirs(os.path.dirname(MAIN_COMPILATION_FILE), exist_ok=True)
        with open(MAIN_COMPILATION_FILE, "w", encoding="utf-8") as f_main_comp:
            f_main_comp.write("我的著作文獻部份\n\n")
        print(f"Initialized {MAIN_COMPILATION_FILE}")
    print("Environment preparation complete.")


def format_basic_data_files(directory_path: str = BASIC_DATA_PATH) -> None:
    if not os.path.isdir(directory_path):
        print(f"Basic data directory not found: {directory_path}")
        return
    source_files = glob.glob(os.path.join(directory_path, "*.txt"))
    for filepath in source_files:
        filename = os.path.basename(filepath)
        if filename.endswith("格式化.txt"):
            continue
        output_filename = filename[:-4] + "格式化.txt"
        output_filepath = os.path.join(directory_path, output_filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f_in:
                content = f_in.read()
            formatted_content = content.replace("  ", " &nbsp; ")
            with open(output_filepath, "w", encoding="utf-8") as f_out:
                f_out.write(formatted_content)
        except (OSError, UnicodeError) as exc:
            print(f"Error formatting file {filepath}: {exc}")


def process_yijing_raw_text() -> bool:
    source_yijing_file = os.path.join(YIJING_INPUT_PATH, "yijing.txt")
    output_processed_file = os.path.join(
        YIJING_ANCIENT_TEXT_PATH,
        "yijing每卦到空列分隔全文文本有分斷點.txt",
    )
    if not os.path.exists(source_yijing_file):
        print(f"Source Yijing file not found: {source_yijing_file}")
        return False
    try:
        os.makedirs(YIJING_ANCIENT_TEXT_PATH, exist_ok=True)
        with open(source_yijing_file, "r", encoding="utf-8") as handle:
            processed_lines = [line for line in handle if line.strip() and line.strip() != "%"]
        content = "".join(processed_lines)
        content = re.sub(r"(《易經》)(.*)", r"\1\n\1\2", content, count=1)
        content = re.sub(r"(彖曰：)(.*)", r"\n\\xxxx\n\1\2", content)
        content = re.sub(r"(象曰：)(.*)", r"\n\\xxx\n\1\2", content)
        content = re.sub(r"(文言曰：)(.*)", r"\n\\xx\n\1\2", content)
        content = re.sub(r"(初.*?：)(.*)", r"\n\\xxxxx\n\1\2", content, count=1)
        with open(output_processed_file, "w", encoding="utf-8") as f_out:
            f_out.write(content)
        print(f"Successfully processed yijing.txt to {output_processed_file}")
        return True
    except (OSError, UnicodeError, re.error) as exc:
        print(f"Error processing yijing.txt: {exc}")
        return False


def generate_yijing_metadata_and_split_guas() -> bool:
    processed_yijing_file = os.path.join(
        YIJING_ANCIENT_TEXT_PATH,
        "yijing每卦到空列分隔全文文本有分斷點.txt",
    )
    if not os.path.exists(processed_yijing_file):
        print(
            f"Processed Yijing file not found: {processed_yijing_file}. "
            "Run process_yijing_raw_text first."
        )
        return False
    try:
        with open(processed_yijing_file, "r", encoding="utf-8") as handle:
            content = handle.read()
        header_pattern = re.compile(r"《易經》(第.*?卦)\s*([^\s]+)\s*([^\s]+)\s*([^\s]+)")
        titles: list[str] = []
        orders: list[str] = []
        order_title_details: list[str] = []
        wisdom_explanations: list[str] = []
        all_lines = content.splitlines()
        header_lines_info: list[dict[str, str | int]] = []
        for line_index, line in enumerate(all_lines):
            match = header_pattern.match(line)
            if not match:
                continue
            order_str, title_str, structure_str, composition_str = (
                match.group(1).strip(),
                match.group(2).strip(),
                match.group(3).strip(),
                match.group(4).strip(),
            )
            orders.append(order_str)
            titles.append(title_str)
            order_title_details.append(f"{order_str} {title_str}")
            wisdom_explanations.append(
                f"啟稟皇上,易經{order_str}是{title_str}卦!,"
                f"本卦看起來是{structure_str}, 由{composition_str}組成!"
            )
            header_lines_info.append(
                {"order": order_str, "title": title_str, "line_index": line_index}
            )
        if not titles:
            print("No Yijing titles found in processed file.")
            return False

        os.makedirs(YIJING_ANCIENT_TEXT_PATH, exist_ok=True)
        metadata = {
            "yijing標題.txt": titles,
            "yijing順序.txt": orders,
            "yijing順序標題.txt": order_title_details,
            "yijing標題列智慧解說.txt": wisdom_explanations,
        }
        for filename, values in metadata.items():
            with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, filename), "w", encoding="utf-8") as handle:
                handle.write("\n".join(values) + "\n")

        for index, current_gua_info in enumerate(header_lines_info):
            start_line_index = int(current_gua_info["line_index"])
            end_line_index = (
                len(all_lines)
                if index + 1 >= len(header_lines_info)
                else int(header_lines_info[index + 1]["line_index"])
            )
            cleaned_gua_lines = [
                line for line in all_lines[start_line_index:end_line_index] if line.strip()
            ]
            output_gua_file = os.path.join(
                YIJING_ANCIENT_TEXT_PATH,
                f"yijing切開第{index + 1}卦古原文無分斷點.txt",
            )
            with open(output_gua_file, "w", encoding="utf-8") as handle:
                handle.write("\n".join(cleaned_gua_lines) + "\n")
        print(f"Successfully generated {len(header_lines_info)} individual gua files.")
        return True
    except Exception as exc:  # Preserve diagnostics for malformed legacy data.
        print(f"Error generating Yijing metadata or splitting guas: {exc}")
        traceback.print_exc()
        return False


def append_ancient_texts_to_compilation() -> None:
    yijing_titles_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    if not os.path.exists(yijing_titles_file):
        print(f"Yijing titles file not found: {yijing_titles_file}. Cannot append ancient texts.")
        return
    with open(yijing_titles_file, "r", encoding="utf-8") as handle:
        titles = [line.strip() for line in handle if line.strip()]
    ancient_texts_content = ["\n以下是易經六十四卦古文原文\n"]
    for index, title in enumerate(titles, start=1):
        gua_file_path = os.path.join(
            YIJING_ANCIENT_TEXT_PATH,
            f"yijing切開第{index}卦古原文無分斷點.txt",
        )
        if os.path.exists(gua_file_path):
            with open(gua_file_path, "r", encoding="utf-8") as gua_file:
                cleaned_gua_text = re.sub(r"\\[xX]+", "", gua_file.read())
            ancient_texts_content.append(
                f"\n--- 第{index}卦 {title} ---\n{cleaned_gua_text}"
            )
        else:
            ancient_texts_content.append(
                f"\n--- 第{index}卦 {title} ---\n古文檔案不存在 ({gua_file_path})\n"
            )
            print(f"Warning: Ancient text file not found for Gua {index} ({title}): {gua_file_path}")
    upsert_text_section(
        MAIN_COMPILATION_FILE,
        "ancient_texts",
        "\n".join(ancient_texts_content),
        initial_header="我的著作文獻部份",
    )
    print(f"Updated Yijing ancient texts in {MAIN_COMPILATION_FILE}")
