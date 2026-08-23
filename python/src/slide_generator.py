# -*- coding: utf-8 -*-
"""Generate impress.js slide data while escaping all file-derived content."""
from __future__ import annotations

import glob
import os
import traceback
from typing import Any

from flask import Blueprint, render_template, url_for
from markupsafe import Markup, escape

from .app_support import text_to_html
from .config import BASIC_DATA_PATH, SLIDES_TEMPLATE_PATH, YIJING_ANCIENT_TEXT_PATH

slides_bp = Blueprint("slides", __name__)

_TITLE_MAP = {
    "執行長學經歷": "竹文診所 - 執行長學經歷",
    "總顧問學經歷": "竹文診所 - 總顧問學經歷",
    "中藥局營業項目": "竹文診所 - 中藥局營業項目",
    "中藥局經營理念": "竹文診所 - 中藥局經營理念",
    "中藥局歷史源流": "竹文診所 - 中藥局歷史源流",
    "中藥局診療日記1090101": "竹文診所 - 中藥局診療日記",
}


def _find_basic_file(index: int) -> tuple[str, str]:
    formatted = sorted(glob.glob(os.path.join(BASIC_DATA_PATH, f"{index:03d}*格式化.txt")))
    candidates = formatted or [
        path
        for path in sorted(glob.glob(os.path.join(BASIC_DATA_PATH, f"{index:03d}*.txt")))
        if not path.endswith("格式化.txt")
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No file matching {index:03d}*.txt found in {BASIC_DATA_PATH}."
        )
    selected = candidates[0]
    basename = os.path.basename(selected).replace("格式化.txt", ".txt")
    stem = os.path.splitext(basename)[0]
    return selected, stem[3:]


def _basic_title(base_name: str) -> str:
    normalized = base_name.replace(" ", "")
    for key, title in _TITLE_MAP.items():
        if key.replace(" ", "") in normalized:
            return title
    return f"竹文診所 - {base_name}"


def _read_titles() -> list[str]:
    titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    if not os.path.isfile(titles_path):
        raise FileNotFoundError(f"Missing Yijing titles file: {titles_path}")
    with open(titles_path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def _read_gua_lines(gua_number: int) -> list[str]:
    gua_file = os.path.join(
        YIJING_ANCIENT_TEXT_PATH,
        f"yijing切開第{gua_number}卦古原文無分斷點.txt",
    )
    if not os.path.isfile(gua_file):
        raise FileNotFoundError(gua_file)
    with open(gua_file, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def _clean_marker(line: str) -> str:
    return line.replace("\\xxxxx", "").replace("\\xxxx", "").replace("\\xxx", "").replace("\\xx", "").strip()


def _extract_tuan_xiang(lines: list[str]) -> tuple[str, str]:
    sections: dict[str, list[str]] = {"tuan": [], "xiang": []}
    current: str | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if line == "\\xxxx":
            current = "tuan"
            continue
        if line == "\\xxx":
            current = "xiang"
            continue
        if line.startswith("\\xx") or line == "\\xxxxx":
            current = None
            continue
        if line.startswith("彖曰："):
            current = "tuan"
            text = line.removeprefix("彖曰：").strip()
            if text:
                sections[current].append(text)
            continue
        if line.startswith("象曰："):
            current = "xiang"
            text = line.removeprefix("象曰：").strip()
            if text:
                sections[current].append(text)
            continue
        if line.startswith("文言曰：") or line.startswith("初"):
            current = None
            continue
        if current and not line.startswith("《易經》"):
            sections[current].append(_clean_marker(line))
    return "\n".join(filter(None, sections["tuan"])), "\n".join(
        filter(None, sections["xiang"])
    )


def _section_html(heading: str, content: str) -> Markup:
    return Markup("<h4>{}</h4><p>{}</p>").format(escape(heading), text_to_html(content))


@slides_bp.get("/lecture_ancient")
def yijing_slides_lecture_ancient():
    slides_data: list[dict[str, Any]] = []
    errors: list[str] = []
    slide_x = 0
    try:
        for index in range(1, 7):
            path, base_name = _find_basic_file(index)
            with open(path, "r", encoding="utf-8") as handle:
                content = text_to_html(handle.read())
            slides_data.append(
                {
                    "title": _basic_title(base_name),
                    "content": content,
                    "data_x": slide_x,
                    "data_y": 0,
                    "data_z": 0,
                    "type": "html_content",
                }
            )
            slide_x += 1200
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        errors.append(f"缺少或無法讀取基本資料：{exc}")

    titles: list[str] = []
    try:
        titles = _read_titles()
        for index, title in enumerate(titles, start=1):
            try:
                lines = [_clean_marker(line) for line in _read_gua_lines(index)]
                body = text_to_html("\n".join(filter(None, lines)))
                intro = Markup("<h3>{}</h3>").format(
                    escape(f"易經第 {index} 卦 {title} 的條文")
                )
                content = intro + body
            except FileNotFoundError:
                content = text_to_html(f"缺少第 {index} 卦（{title}）的古文檔案。")
            slides_data.append(
                {
                    "title": f"易經古文解析 - 第{index}卦 {title}",
                    "content": content,
                    "data_x": ((index - 1) % 8) * 1200,
                    "data_y": 800 + ((index - 1) // 8) * 800,
                    "data_z": 0,
                    "type": "html_content",
                }
            )
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        errors.append(f"無法讀取易經資料：{exc}")

    return render_template(
        "slides_yijing_lecture.html",
        slides_data=slides_data,
        error_message="\n".join(errors) or None,
        title="易經古文解析講座",
        overview_x=3500,
        overview_y=1500 + ((len(titles) // 8) * 400 if titles else 0),
        overview_scale=10 if slides_data else 1,
    )


@slides_bp.get("/lecture_guaci_moms_records")
def yijing_slides_lecture_guaci_moms_records():
    slides_data: list[dict[str, Any]] = []
    errors: list[str] = []
    slide_x = 0
    slide_y = 0
    row_spacing = 800
    col_spacing = 1200

    def add_slide(
        title: str,
        content: Markup | str,
        *,
        slide_type: str = "html_content",
        image_url: str | None = None,
        video_url: str | None = None,
    ) -> None:
        nonlocal slide_x
        slides_data.append(
            {
                "title": title,
                "content": content,
                "type": slide_type,
                "image_url": image_url,
                "video_url": video_url,
                "data_x": slide_x,
                "data_y": slide_y,
                "data_z": 0,
            }
        )
        slide_x += col_spacing

    def next_row() -> None:
        nonlocal slide_x, slide_y
        slide_x = 0
        slide_y += row_spacing

    add_slide(
        "出版資訊",
        Markup("<p>出版者：竹文出版社</p><p>發行者：竹文資訊</p><p>總經銷：竹文堂</p>"),
    )
    next_row()

    for index in range(1, 7):
        try:
            path, base_name = _find_basic_file(index)
            with open(path, "r", encoding="utf-8") as handle:
                add_slide(_basic_title(base_name), text_to_html(handle.read()))
        except (FileNotFoundError, OSError, UnicodeError) as exc:
            errors.append(str(exc))
    next_row()

    for pattern, label in (("b[0-9]*.jpg", "媽手記相片"), ("c[0-9]*.jpg", "生活剪影")):
        matched = sorted(glob.glob(os.path.join(SLIDES_TEMPLATE_PATH, pattern)))
        for photo_path in matched:
            filename = os.path.basename(photo_path)
            add_slide(
                f"{label} - {filename}",
                "",
                slide_type="image",
                image_url=url_for("static", filename=f"slides_assets/{filename}"),
            )
        if matched:
            next_row()

    for filename, title in (
        ("記事本程式.txt", "記事本摘要"),
        ("媽文章程式.txt", "媽文章"),
        ("我演講程式.txt", "演講紀錄"),
        ("變色盤程式.txt", "變色盤參考"),
    ):
        path = os.path.join(SLIDES_TEMPLATE_PATH, filename)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    add_slide(title, text_to_html(handle.read()))
                next_row()
            except (OSError, UnicodeError) as exc:
                errors.append(f"無法讀取 {filename}：{exc}")

    try:
        titles = _read_titles()
        for index, title in enumerate(titles, start=1):
            try:
                tuan_text, xiang_text = _extract_tuan_xiang(_read_gua_lines(index))
            except FileNotFoundError:
                errors.append(f"缺少第 {index} 卦（{title}）古文檔案。")
                continue
            content = Markup("")
            if tuan_text:
                content += _section_html("彖辭", tuan_text)
            if xiang_text:
                content += _section_html("象辭", xiang_text)
            if content:
                add_slide(f"易經卦解 - 第{index}卦 {title}（彖／象）", content)
                if index % 4 == 0:
                    next_row()
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        errors.append(str(exc))

    return render_template(
        "slides_yijing_guaci_moms_records.html",
        slides_data=slides_data,
        error_message="\n".join(errors) or None,
        title="易經卦辭與媽傳記講座",
        overview_x=3000,
        overview_y=slide_y / 2 if slide_y else 1500,
        overview_scale=8 if slides_data else 1,
    )


@slides_bp.get("/lecture_tuanxiang")
def yijing_slides_lecture_tuanxiang():
    slides_data: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        for index, title in enumerate(_read_titles(), start=1):
            try:
                tuan_text, xiang_text = _extract_tuan_xiang(_read_gua_lines(index))
            except FileNotFoundError:
                errors.append(f"缺少第 {index} 卦（{title}）古文檔案。")
                continue
            for section_name, content in (("彖辭", tuan_text), ("象辭", xiang_text)):
                if not content:
                    continue
                slide_index = len(slides_data)
                slides_data.append(
                    {
                        "title": f"{title}（第{index}卦）- {section_name}",
                        "content": text_to_html(content),
                        "type": "html_content",
                        "data_x": (slide_index % 4) * 1200,
                        "data_y": (slide_index // 4) * 800,
                        "data_z": 0,
                    }
                )
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        errors.append(str(exc))
    except Exception:
        traceback.print_exc()
        errors.append("產生彖象投影片時發生未預期錯誤。")

    rows = (len(slides_data) + 3) // 4
    return render_template(
        "slides_yijing_tuanxiang.html",
        slides_data=slides_data,
        error_message="\n".join(errors) or None,
        title="易經彖象解析講座",
        overview_x=1800,
        overview_y=max(1000, rows * 400),
        overview_scale=6 if slides_data else 1,
    )
