# -*- coding: utf-8 -*-
"""Flask blueprints for Yijing and fengshui content pages."""
from __future__ import annotations

import os
import re
from urllib.parse import quote, quote_plus

from flask import Blueprint, abort, render_template

from .app_support import resolve_existing_child
from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH, YIJING_WIKI_GUA_CLEANED_PATH
from .content_catalog import build_content_catalog
from .wiki_handler import safe_filename


gua_bp = Blueprint("gua", __name__)
fengshui_bp = Blueprint("fengshui", __name__)


def _load_gua_data(gua_number: int, title: str) -> dict[str, object]:
    ancient_text_file = os.path.join(
        YIJING_ANCIENT_TEXT_PATH,
        f"yijing切開第{gua_number}卦古原文無分斷點.txt",
    )
    if os.path.isfile(ancient_text_file):
        with open(ancient_text_file, "r", encoding="utf-8") as handle:
            ancient_text = "\n".join(
                re.sub(r"\\[xX]+", "", line).strip() for line in handle if line.strip()
            )
    else:
        ancient_text = "古文資料不存在。"

    wiki_content_file = os.path.join(
        YIJING_WIKI_GUA_CLEANED_PATH,
        f"yijing卦名維基文獻第{gua_number}條{safe_filename(title)}粗掃.txt",
    )
    if os.path.isfile(wiki_content_file):
        with open(wiki_content_file, "r", encoding="utf-8") as handle:
            wiki_lines = [line.strip() for line in handle if line.strip()]
        wiki_content = "\n".join(wiki_lines[1:])
    else:
        wiki_content = "維基百科資料不存在或尚未處理。"

    return {
        "title": title,
        "gua_number": gua_number,
        "ancient_text": ancient_text,
        "wiki_content": wiki_content,
        "external_links": [
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
        ],
    }


@gua_bp.get("/<int:gua_number>")
def gua_page(gua_number: int):
    if not 1 <= gua_number <= 64:
        abort(404)
    catalog = build_content_catalog()
    entry = catalog.find("gua", str(gua_number))
    if entry is None:
        abort(404)
    previous_entry, next_entry = catalog.adjacent("gua", entry.key)
    return render_template(
        "gua_page.html",
        gua_data=_load_gua_data(gua_number, entry.title),
        previous_entry=previous_entry,
        next_entry=next_entry,
        site_title="易經研讀室",
    )


@fengshui_bp.get("/case/<path:case_filename>")
def fengshui_case_page(case_filename: str):
    key = case_filename.removesuffix(".txt")
    entry = build_content_catalog().find("fengshui_case", key)
    if entry is None or not entry.available:
        abort(404)
    try:
        case_file = resolve_existing_child(YIJING_INPUT_PATH, key, suffixes=(".txt", ""))
    except (FileNotFoundError, ValueError):
        abort(404)
    case_data = {"title": case_file.stem, "content": case_file.read_text(encoding="utf-8")}
    return render_template(
        "fengshui_case_page.html",
        case_data=case_data,
        site_title="易經研讀室",
    )
