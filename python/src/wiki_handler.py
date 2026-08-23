# -*- coding: utf-8 -*-
"""Download and clean Wikipedia material used by the application."""
from __future__ import annotations

import os
import re
import traceback
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .file_utils import upsert_text_section

from .config import (
    MAIN_COMPILATION_FILE,
    YIJING_ANCIENT_TEXT_PATH,
    YIJING_INPUT_PATH,
    YIJING_WIKI_GUA_CLEANED_PATH,
    YIJING_WIKI_GUA_RAW_PATH,
    YIJING_WIKI_RESULT_PATH,
    YIJING_WIKI_TEMP_PATH,
)

WIKIPEDIA_USER_AGENT = os.environ.get(
    "DAD_WIKIPEDIA_USER_AGENT",
    "dad-yijing-app/1.0 (local research tool; contact: repository owner)",
)


def safe_filename(value: str, fallback: str = "untitled") -> str:
    """Return a cross-platform filename fragment without path traversal."""
    cleaned = re.sub(r"[\\/\x00-\x1f\x7f]+", "_", value).strip(" ._")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120] or fallback


def _ensure_parent(path: str | os.PathLike[str]) -> None:
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def get_wiki_content_basic(
    topic_name: str,
    raw_save_path: str | None = None,
    cleaned_save_path: str | None = None,
) -> str | None:
    topic_name = topic_name.strip()
    if not topic_name:
        raise ValueError("Wikipedia topic cannot be empty")
    url = f"https://zh.wikipedia.org/zh-tw/{quote(topic_name, safe='')}"
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": WIKIPEDIA_USER_AGENT},
        )
        response.raise_for_status()
        if raw_save_path:
            _ensure_parent(raw_save_path)
            with open(raw_save_path, "w", encoding="utf-8") as f_raw:
                f_raw.write(response.text)

        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        for selector in (
            ".mw-editsection",
            ".reference",
            ".toc",
            ".infobox",
            ".thumb",
            ".mw-indicators",
        ):
            for tag in soup.select(selector):
                tag.decompose()

        content_div = (
            soup.find("div", id="mw-content-text")
            or soup.find("div", id="bodyContent")
            or soup.find("main", id="content")
        )
        if content_div:
            elements = content_div.find_all(
                ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
            )
            text_content = "\n".join(
                element.get_text(separator=" ", strip=True) for element in elements
            )
        else:
            text_content = soup.get_text(separator="\n", strip=True)
        cleaned_text = "\n".join(
            line.strip() for line in text_content.splitlines() if line.strip()
        )

        if cleaned_save_path:
            _ensure_parent(cleaned_save_path)
            with open(cleaned_save_path, "w", encoding="utf-8") as f_cleaned:
                f_cleaned.write(f"以下是{topic_name}維基網資料\n")
                f_cleaned.write(cleaned_text + "\n")
        return cleaned_text
    except requests.exceptions.RequestException as exc:
        print(f"Error fetching Wikipedia page for {topic_name}: {exc}")
        return None
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error processing Wikipedia page for {topic_name}: {exc}")
        traceback.print_exc()
        return None


def _selected_items(items: list[str], begin_line: int, end_line: int) -> list[str]:
    if begin_line < 1 or end_line < begin_line:
        raise ValueError("The selected line range is invalid")
    return items[begin_line - 1 : end_line]


def process_custom_topics_wiki(begin_line: int = 1, end_line: int = 1) -> bool:
    custom_topics_file = os.path.join(YIJING_INPUT_PATH, "易經自選專有名詞.txt")
    output_literature_file = os.path.join(
        YIJING_WIKI_RESULT_PATH,
        "自選專有名詞維基文獻.txt",
    )
    if not os.path.exists(custom_topics_file):
        print(f"Custom topics file not found: {custom_topics_file}")
        return False
    with open(custom_topics_file, "r", encoding="utf-8") as handle:
        all_topics = [line.strip() for line in handle if line.strip()]
    selected_topics = _selected_items(all_topics, begin_line, end_line)
    if not selected_topics:
        print("No custom Wikipedia topics were selected.")
        return False

    all_wiki_content_for_compilation = ["這是本王自選標題維基資料下載\n"]
    for absolute_index, topic in enumerate(selected_topics, start=begin_line):
        filename_topic = safe_filename(topic)
        cleaned_topic_path = os.path.join(
            YIJING_WIKI_TEMP_PATH,
            "5",
            f"自選專有名詞維基文獻第{absolute_index}條{filename_topic}粗掃.txt",
        )
        raw_text = get_wiki_content_basic(topic, cleaned_save_path=cleaned_topic_path)
        content = raw_text if raw_text else "Failed to retrieve content."
        all_wiki_content_for_compilation.append(
            f"這是本王的資料---{topic}---\n{content}\n"
        )

    os.makedirs(YIJING_WIKI_RESULT_PATH, exist_ok=True)
    with open(output_literature_file, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(all_wiki_content_for_compilation))
    upsert_text_section(
        MAIN_COMPILATION_FILE,
        "custom_topics_wiki",
        "以下是風水專有名詞維基文獻\n\n"
        + "\n".join(all_wiki_content_for_compilation),
        initial_header="我的著作文獻部份",
    )
    return True


def process_yijing_guas_wiki() -> bool:
    yijing_titles_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    output_literature_file = os.path.join(
        YIJING_WIKI_RESULT_PATH,
        "yijing卦名維基文獻.txt",
    )
    if not os.path.exists(yijing_titles_file):
        print(f"Yijing titles file not found: {yijing_titles_file}")
        return False
    with open(yijing_titles_file, "r", encoding="utf-8") as handle:
        gua_titles = [line.strip() for line in handle if line.strip()]
    if not gua_titles:
        print("No Yijing titles were found.")
        return False

    all_gua_wiki_content_for_compilation = ["這是本王易經標題維基資料下載\n"]
    for index, gua_title in enumerate(gua_titles, start=1):
        filename_title = safe_filename(gua_title)
        raw_gua_path = os.path.join(
            YIJING_WIKI_GUA_RAW_PATH,
            f"yijing卦名維基文獻粗1第{index}條{filename_title}.txt",
        )
        cleaned_gua_path = os.path.join(
            YIJING_WIKI_GUA_CLEANED_PATH,
            f"yijing卦名維基文獻第{index}條{filename_title}粗掃.txt",
        )
        raw_text = get_wiki_content_basic(
            gua_title,
            raw_save_path=raw_gua_path,
            cleaned_save_path=cleaned_gua_path,
        )
        content = raw_text if raw_text else "Failed to retrieve content."
        all_gua_wiki_content_for_compilation.append(
            f"這是本王的資料---{gua_title}---\n{content}\n"
        )

    os.makedirs(YIJING_WIKI_RESULT_PATH, exist_ok=True)
    with open(output_literature_file, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(all_gua_wiki_content_for_compilation))
    upsert_text_section(
        MAIN_COMPILATION_FILE,
        "yijing_gua_wiki",
        "以下是易經卦名維基文獻\n\n"
        + "\n".join(all_gua_wiki_content_for_compilation),
        initial_header="我的著作文獻部份",
    )
    return True
