# -*- coding: utf-8 -*-
import os
import glob
import re
import shutil
import traceback
from .config import (
    BASH_SOURCE_DIR, CONFIG_DATA_PATH, YIJING_INPUT_PATH, YIJING_ANCIENT_TEXT_PATH,
    BASIC_DATA_PATH, TOOL_DATA_PATH, HTML_TEMPLATE_PATH, SLIDES_TEMPLATE_PATH, M_TXT_PATH,
    FENGSHUI_CASES_PATH, YIJING_TOTAL_RESULT_PATH, YIJING_RESULT_PATH, YIJING_INTERMEDIATE_PATH,
    YIJING_MARKING_PATH, YIJING_WIKI_RESULT_PATH, YIJING_HTML_RESULT_PATH, YIJING_SLIDES_RESULT_PATH,
    YIJING_WIKI_TEMP_PATH, YIJING_ANCIENT_TEMP_PATH, YIJING_HTML_TEMP_PATH, YIJING_SLIDES_TEMP_PATH,
    YIJING_WIKI_GUA_RAW_PATH, YIJING_WIKI_GUA_CLEANED_PATH, MAIN_COMPILATION_FILE
)

def prepare_environment():
    print("Preparing environment...")
    os.makedirs(CONFIG_DATA_PATH, exist_ok=True)
    dirs_to_copy = {
        "基本資料資料夾": BASIC_DATA_PATH,
        "易經輸入端資料夾": YIJING_INPUT_PATH,
        "工具程式資料夾": TOOL_DATA_PATH,
        "HTML參考樣板資料夾": HTML_TEMPLATE_PATH,
        "投影片參考樣板資料夾": SLIDES_TEMPLATE_PATH,
        "易經個案資料夾": FENGSHUI_CASES_PATH
    }
    for src_dirname, dest_path in dirs_to_copy.items():
        src_path = os.path.join(BASH_SOURCE_DIR, src_dirname)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"Warning: Source directory {src_path} not found.")
            os.makedirs(dest_path, exist_ok=True)
    m_txt_src = os.path.join(BASH_SOURCE_DIR, "m.txt")
    if os.path.exists(m_txt_src):
        shutil.copy2(m_txt_src, M_TXT_PATH)
        print(f"Copied {m_txt_src} to {M_TXT_PATH}")
    else:
        print(f"Warning: Source file {m_txt_src} not found.")
    dirs_to_create = [
        YIJING_TOTAL_RESULT_PATH, YIJING_RESULT_PATH, YIJING_INTERMEDIATE_PATH, YIJING_MARKING_PATH,
        YIJING_WIKI_RESULT_PATH, YIJING_ANCIENT_TEXT_PATH, YIJING_HTML_RESULT_PATH, YIJING_SLIDES_RESULT_PATH,
        YIJING_WIKI_TEMP_PATH, YIJING_ANCIENT_TEMP_PATH, YIJING_HTML_TEMP_PATH, YIJING_SLIDES_TEMP_PATH,
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果1資料夾"),
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果2資料夾"),
        YIJING_WIKI_GUA_RAW_PATH, YIJING_WIKI_GUA_CLEANED_PATH
    ]
    for path_to_create in dirs_to_create:
        os.makedirs(path_to_create, exist_ok=True)
    for i in range(1, 7):
        os.makedirs(os.path.join(YIJING_WIKI_TEMP_PATH, str(i)), exist_ok=True)
    if not os.path.exists(MAIN_COMPILATION_FILE) or os.path.getsize(MAIN_COMPILATION_FILE) == 0:
        with open(MAIN_COMPILATION_FILE, "w", encoding="utf-8") as f_main_comp:
            f_main_comp.write("我的著作文獻部份\n\n")
            print(f"Initialized {MAIN_COMPILATION_FILE}")
    print("Environment preparation complete.")

def format_basic_data_files(directory_path = BASIC_DATA_PATH):
    if not os.path.isdir(directory_path):
        print(f"Basic data directory not found: {directory_path}")
        return
    source_files = glob.glob(os.path.join(directory_path, "*.txt"))
    for filepath in source_files:
        filename = os.path.basename(filepath)
        if filename.endswith("格式化.txt"):
            continue
        if filename.endswith(".txt") and os.path.isfile(filepath):
            output_filename = filename[:-4] + "格式化.txt"
            output_filepath = os.path.join(directory_path, output_filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f_in:
                    content = f_in.read()
                formatted_content = content.replace("  ", " &nbsp; ")
                with open(output_filepath, "w", encoding="utf-8") as f_out:
                    f_out.write(formatted_content)
            except Exception as e:
                print(f"Error formatting file {filepath}: {e}")

def process_yijing_raw_text():
    source_yijing_file = os.path.join(YIJING_INPUT_PATH, "yijing.txt")
    output_processed_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing每卦到空列分隔全文文本有分斷點.txt")
    if not os.path.exists(source_yijing_file):
        print(f"Source Yijing file not found: {source_yijing_file}")
        return False
    try:
        with open(source_yijing_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        processed_lines = [line for line in lines if line.strip()]
        temp_lines = []
        for line in processed_lines:
            if line.strip() != '%':
                temp_lines.append(line)
        processed_lines = temp_lines
        content = "".join(processed_lines)
        content = re.sub(r"(《易經》)(.*)", r"\1\n\1\2", content, 1)
        content = re.sub(r"(彖曰：)(.*)", r"\n\\xxxx\n\1\2", content)
        content = re.sub(r"(象曰：)(.*)", r"\n\\xxx\n\1\2", content)
        content = re.sub(r"(文言曰：)(.*)", r"\n\\xx\n\1\2", content)
        content = re.sub(r"(初.*?：)(.*)", r"\n\\xxxxx\n\1\2", content, 1)
        with open(output_processed_file, "w", encoding="utf-8") as f_out:
            f_out.write(content)
        print(f"Successfully processed yijing.txt to {output_processed_file}")
        return True
    except Exception as e:
        print(f"Error processing yijing.txt: {e}")
        return False

def generate_yijing_metadata_and_split_guas():
    processed_yijing_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing每卦到空列分隔全文文本有分斷點.txt")
    if not os.path.exists(processed_yijing_file):
        print(f"Processed Yijing file not found: {processed_yijing_file}. Run process_yijing_raw_text first.")
        return False
    try:
        with open(processed_yijing_file, "r", encoding="utf-8") as f:
            content = f.read()
        header_pattern = re.compile(r"《易經》(第.*?卦)\s*([^\s]+)\s*([^\s]+)\s*([^\s]+)")
        titles, orders, order_title_details, wisdom_explanations = [], [], [], []
        all_lines = content.splitlines()
        header_lines_info = []
        for i, line in enumerate(all_lines):
            match = header_pattern.match(line)
            if match:
                order_str, title_str, structure_str, composition_str = (match.group(1).strip(), match.group(2).strip(), match.group(3).strip(), match.group(4).strip())
                orders.append(order_str)
                titles.append(title_str)
                order_title_details.append(f"{order_str} {title_str}")
                wisdom_explanations.append(f"啟稟皇上,易經{order_str}是{title_str}卦!,本卦看起來是{structure_str}, 由{composition_str}組成!")
                header_lines_info.append({"order": order_str, "title": title_str, "line_index": i})
        if not titles:
            print("No Yijing titles found in processed file.")
            return False
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt"), "w", encoding="utf-8") as f_out: f_out.write("\n".join(titles) + "\n")
        print(f"Successfully generated yijing標題.txt")
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing順序.txt"), "w", encoding="utf-8") as f_out: f_out.write("\n".join(orders) + "\n")
        print(f"Successfully generated yijing順序.txt")
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing順序標題.txt"), "w", encoding="utf-8") as f_out: f_out.write("\n".join(order_title_details) + "\n")
        print(f"Successfully generated yijing順序標題.txt")
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題列智慧解說.txt"), "w", encoding="utf-8") as f_out: f_out.write("\n".join(wisdom_explanations) + "\n")
        print(f"Successfully generated yijing標題列智慧解說.txt")
        for i in range(len(header_lines_info)):
            current_gua_info = header_lines_info[i]
            start_line_index = current_gua_info["line_index"]
            end_line_index = len(all_lines) if i + 1 >= len(header_lines_info) else header_lines_info[i+1]["line_index"]
            gua_block_lines = all_lines[start_line_index:end_line_index]
            cleaned_gua_lines = [line for line in gua_block_lines if line.strip()]
            output_gua_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{i+1}卦古原文無分斷點.txt")
            with open(output_gua_file, "w", encoding="utf-8") as f_gua: f_gua.write("\n".join(cleaned_gua_lines) + "\n")
        print(f"Successfully generated 64 individual gua files.")
        return True
    except Exception as e:
        print(f"Error generating Yijing metadata or splitting guas: {e}")
        traceback.print_exc()
        return False

def append_ancient_texts_to_compilation():
    yijing_titles_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    if not os.path.exists(yijing_titles_file):
        print(f"Yijing titles file not found: {yijing_titles_file}. Cannot append ancient texts.")
        return
    with open(yijing_titles_file, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]
    ancient_texts_content = ["\n以下是易經六十四卦古文原文\n"]
    for i, title in enumerate(titles):
        gua_num = i + 1
        gua_file_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_num}卦古原文無分斷點.txt")
        if os.path.exists(gua_file_path):
            with open(gua_file_path, "r", encoding="utf-8") as gf:
                gua_text = gf.read()
                cleaned_gua_text = re.sub(r"\\[xX]+", "", gua_text)
                ancient_texts_content.append(f"\n--- 第{gua_num}卦 {title} ---\n{cleaned_gua_text}")
        else:
            ancient_texts_content.append(f"\n--- 第{gua_num}卦 {title} ---\n古文檔案不存在 ({gua_file_path})\n")
            print(f"Warning: Ancient text file not found for Gua {gua_num} ({title}): {gua_file_path}")
    with open(MAIN_COMPILATION_FILE, "a", encoding="utf-8") as f_main_comp:
        f_main_comp.write("\n".join(ancient_texts_content) + "\n")
    print(f"Appended Yijing ancient texts to {MAIN_COMPILATION_FILE}")

