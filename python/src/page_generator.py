# -*- coding: utf-8 -*-
"""Flask blueprints for Yijing and fengshui content pages."""
from __future__ import annotations

import os
import re
import traceback
from urllib.parse import quote, quote_plus

from flask import Blueprint, render_template

from .app_support import resolve_existing_child
from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH, YIJING_WIKI_GUA_CLEANED_PATH
from .wiki_handler import safe_filename


gua_bp = Blueprint("gua", __name__)
fengshui_bp = Blueprint("fengshui", __name__)


@gua_bp.get("/<int:gua_number>")
def gua_page(gua_number: int):
    error_message = None
    gua_data: dict[str, object] = {}
    try:
        if not 1 <= gua_number <= 64:
            raise ValueError("卦序必須介於 1 到 64 之間。")
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if not os.path.isfile(titles_path):
            raise FileNotFoundError("yijing標題.txt 檔案不存在。")
        with open(titles_path, "r", encoding="utf-8") as handle:
            all_titles = [line.strip() for line in handle if line.strip()]
        if gua_number > len(all_titles):
            raise ValueError(f"目前只有 {len(all_titles)} 卦的標題資料。")

        title = all_titles[gua_number - 1]
        gua_data.update(title=title, gua_number=gua_number)

        ancient_text_file = os.path.join(
            YIJING_ANCIENT_TEXT_PATH,
            f"yijing切開第{gua_number}卦古原文無分斷點.txt",
        )
        if os.path.isfile(ancient_text_file):
            with open(ancient_text_file, "r", encoding="utf-8") as handle:
                gua_data["ancient_text"] = "\n".join(
                    re.sub(r"\\[xX]+", "", line).strip()
                    for line in handle
                    if line.strip()
                )
        else:
            gua_data["ancient_text"] = "古文資料不存在。"

        filename_title = safe_filename(title)
        wiki_content_file = os.path.join(
            YIJING_WIKI_GUA_CLEANED_PATH,
            f"yijing卦名維基文獻第{gua_number}條{filename_title}粗掃.txt",
        )
        if os.path.isfile(wiki_content_file):
            with open(wiki_content_file, "r", encoding="utf-8") as handle:
                wiki_lines = [line.strip() for line in handle if line.strip()]
            gua_data["wiki_content"] = "\n".join(wiki_lines[1:])
        else:
            gua_data["wiki_content"] = "維基百科資料不存在或尚未處理。"

        gua_data["external_links"] = [
            {
                "name": "Google 搜尋",
                "url": f"https://www.google.com/search?q={quote_plus(f'易經 {title}')}",
            },
            {
                "name": "百度搜尋",
                "url": f"https://www.baidu.com/s?wd={quote_plus(f'易经 {title}')}",
            },
            {
                "name": "維基百科",
                "url": f"https://zh.wikipedia.org/wiki/{quote(title, safe='')}",
            },
        ]
    except (FileNotFoundError, ValueError) as exc:
        error_message = str(exc)
    except Exception as exc:
        error_message = f"載入卦頁面時發生錯誤：{exc}"
        traceback.print_exc()
    return render_template(
        "gua_page.html",
        gua_data=gua_data,
        error_message=error_message,
        site_title="易經互動網頁",
    )


@fengshui_bp.get("/case/<path:case_filename>")
def fengshui_case_page(case_filename: str):
    error_message = None
    case_data: dict[str, str] = {}
    try:
        case_file = resolve_existing_child(
            YIJING_INPUT_PATH,
            case_filename,
            suffixes=(".txt", ""),
        )
        with case_file.open("r", encoding="utf-8") as handle:
            case_content = handle.read()
        case_data["title"] = case_file.stem
        case_data["content"] = case_content
    except (FileNotFoundError, ValueError) as exc:
        error_message = f"資料檔案無法讀取：{exc}"
    except Exception as exc:
        error_message = f"載入風水個案頁面時發生錯誤：{exc}"
        traceback.print_exc()
    return render_template(
        "fengshui_case_page.html",
        case_data=case_data,
        error_message=error_message,
        site_title="易經互動網頁",
    )
