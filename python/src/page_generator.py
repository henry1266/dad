# -*- coding: utf-8 -*-
import os
import re
import traceback
from flask import Blueprint, render_template, url_for
from .config import (
    YIJING_ANCIENT_TEXT_PATH, YIJING_WIKI_GUA_CLEANED_PATH, FENGSHUI_CASES_PATH, YIJING_INPUT_PATH
)

gua_bp = Blueprint("gua", __name__, template_folder="../templates", static_folder="../static")
fengshui_bp = Blueprint("fengshui", __name__, template_folder="../templates", static_folder="../static")

@gua_bp.route("/<int:gua_number>")
def gua_page(gua_number):
    error_message = None
    gua_data = {}
    try:
        if not 1 <= gua_number <= 64:
            raise ValueError("卦序必須介於1到64之間")
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if not os.path.exists(titles_path):
            raise FileNotFoundError("yijing標題.txt 檔案不存在")
        with open(titles_path, "r", encoding="utf-8") as f:
            all_titles = [line.strip() for line in f if line.strip()]
        gua_data["title"] = all_titles[gua_number - 1] if len(all_titles) >= gua_number else f"第{gua_number}卦"
        gua_data["gua_number"] = gua_number
        ancient_text_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_number}卦古原文無分斷點.txt")
        if not os.path.exists(ancient_text_file):
            gua_data["ancient_text"] = "古文資料不存在。"
        else:
            with open(ancient_text_file, "r", encoding="utf-8") as f:
                ancient_lines = [re.sub(r"\\[xX]+", "", line).strip() for line in f.readlines() if line.strip()]
                gua_data["ancient_text"] = "<br>".join(ancient_lines)
        wiki_content_file = os.path.join(YIJING_WIKI_GUA_CLEANED_PATH, f"yijing卦名維基文獻第{gua_number}條{gua_data['title']}粗掃.txt")
        if not os.path.exists(wiki_content_file):
            gua_data["wiki_content"] = "維基百科資料不存在或尚未處理。"
        else:
            with open(wiki_content_file, "r", encoding="utf-8") as f:
                wiki_lines = f.readlines()
                # Skip the header line like "以下是乾維基網資料"
                gua_data["wiki_content"] = "<br>".join([line.strip() for line in wiki_lines[1:] if line.strip()])
        gua_name_for_url = gua_data["title"]
        gua_data["external_links"] = [
            {"name": "谷歌搜尋", "url": f"https://www.google.com/search?q=易經+{gua_name_for_url}"},
            {"name": "百度搜尋", "url": f"https://www.baidu.com/s?wd=易经+{gua_name_for_url}"},
            {"name": "維基百科", "url": f"https://zh.wikipedia.org/wiki/{gua_name_for_url}"},
        ]
    except FileNotFoundError as e:
        error_message = f"資料檔案遺失: {str(e)}"
    except ValueError as e:
        error_message = str(e)
    except Exception as e:
        error_message = f"載入卦頁面時發生錯誤: {str(e)}"
        traceback.print_exc()
    return render_template("gua_page.html", gua_data=gua_data, error_message=error_message, site_title="易經互動網頁")

@fengshui_bp.route("/case/<case_filename>")
def fengshui_case_page(case_filename):
    error_message = None
    case_data = {}
    try:
        # Construct the full path to the case file, assuming it ends with .txt
        case_file_path = os.path.join(FENGSHUI_CASES_PATH, case_filename + ".txt")
        if not os.path.exists(case_file_path):
            # Try without .txt if the filename already includes it (though the route implies it doesn't)
            case_file_path_alt = os.path.join(FENGSHUI_CASES_PATH, case_filename)
            if not os.path.exists(case_file_path_alt):
                 raise FileNotFoundError(f"個案檔案 {case_filename} 或 {case_filename}.txt 不存在於 {FENGSHUI_CASES_PATH}")
            case_file_path = case_file_path_alt # Use the one that exists
        
        with open(case_file_path, "r", encoding="utf-8") as f:
            case_content = f.read()
        
        # Use the filename (without .txt if it was added) as the title
        display_title = case_filename.replace(".txt", "")
        case_data["title"] = display_title
        case_data["content"] = case_content

    except FileNotFoundError as e:
        error_message = f"資料檔案遺失: {str(e)}"
    except Exception as e:
        error_message = f"載入風水個案頁面時發生錯誤: {str(e)}"
        traceback.print_exc()

    return render_template("fengshui_case_page.html", case_data=case_data, error_message=error_message, site_title="易經互動網頁")

