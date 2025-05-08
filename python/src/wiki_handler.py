# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import traceback
from .config import (
    YIJING_INPUT_PATH, YIJING_WIKI_RESULT_PATH, YIJING_TOTAL_RESULT_PATH, 
    YIJING_WIKI_TEMP_PATH, YIJING_ANCIENT_TEXT_PATH, YIJING_WIKI_GUA_RAW_PATH, 
    YIJING_WIKI_GUA_CLEANED_PATH, MAIN_COMPILATION_FILE
)

def get_wiki_content_basic(topic_name, raw_save_path=None, cleaned_save_path=None):
    url = f"http://zh.wikipedia.org/zh-tw/{topic_name}"
    text_content = ""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        if raw_save_path:
            with open(raw_save_path, "w", encoding="utf-8") as f_raw:
                f_raw.write(response.text)
            print(f"Saved raw Wikipedia content for {topic_name} to {raw_save_path}")
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", ".mw-editsection", ".reference", ".toc", ".infobox", ".thumb", ".mw-indicators"]):
            tag.decompose()
        content_div = soup.find('div', id='mw-content-text') or soup.find('div', id='bodyContent') or soup.find('main', id='content')
        if content_div:
            for element in content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text_content += element.get_text(separator=' ', strip=True) + "\n"
        else:
            text_content = soup.get_text(separator=' ', strip=True)
        cleaned_text = "\n".join([line for line in text_content.splitlines() if line.strip()])
        if cleaned_save_path:
            with open(cleaned_save_path, "w", encoding="utf-8") as f_cleaned:
                f_cleaned.write(f"以下是{topic_name}維基網資料\n")
                f_cleaned.write(cleaned_text + "\n")
            print(f"Saved cleaned Wikipedia content for {topic_name} to {cleaned_save_path}")
        return cleaned_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia page for {topic_name}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in get_wiki_content_basic for {topic_name}: {e}")
        traceback.print_exc()
        return None

def process_custom_topics_wiki(begin_line=1, end_line=1):
    custom_topics_file = os.path.join(YIJING_INPUT_PATH, "易經自選專有名詞.txt")
    output_literature_file = os.path.join(YIJING_WIKI_RESULT_PATH, "自選專有名詞維基文獻.txt")
    if not os.path.exists(custom_topics_file):
        print(f"Custom topics file not found: {custom_topics_file}"); return
    with open(custom_topics_file, "r", encoding="utf-8") as f:
        all_topics = [line.strip() for line in f if line.strip()]
    selected_topics = all_topics[begin_line-1:end_line]
    print(f"Fetching Wikipedia data for custom topics: {', '.join(selected_topics)}")
    all_wiki_content_for_compilation = ["這是本王自選標題維基資料下載\n"]
    for i, topic in enumerate(selected_topics):
        print(f"Processing topic {i+1}/{len(selected_topics)}: {topic}")
        cleaned_topic_path = os.path.join(YIJING_WIKI_TEMP_PATH, "5", f"自選專有名詞維基文獻第{i+1}條{topic}粗掃.txt")
        raw_text = get_wiki_content_basic(topic, cleaned_save_path=cleaned_topic_path)
        if raw_text:
            all_wiki_content_for_compilation.append(f"這是本王的資料---{topic}---\n{raw_text}\n")
        else:
            all_wiki_content_for_compilation.append(f"這是本王的資料---{topic}---\nFailed to retrieve content.\n")
    with open(output_literature_file, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(all_wiki_content_for_compilation))
    print(f"Successfully generated {output_literature_file}")
    with open(MAIN_COMPILATION_FILE, "a", encoding="utf-8") as f_main_comp:
        f_main_comp.write("\n以下是風水專有名詞維基文獻\n\n" + "\n".join(all_wiki_content_for_compilation) + "\n")
    print(f"Appended custom topics to {MAIN_COMPILATION_FILE}")

def process_yijing_guas_wiki():
    yijing_titles_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    output_literature_file = os.path.join(YIJING_WIKI_RESULT_PATH, "yijing卦名維基文獻.txt")
    if not os.path.exists(yijing_titles_file):
        print(f"Yijing titles file not found: {yijing_titles_file}"); return
    with open(yijing_titles_file, "r", encoding="utf-8") as f:
        gua_titles = [line.strip() for line in f if line.strip()]
    print(f"Fetching Wikipedia data for {len(gua_titles)} Yijing Guas...")
    all_gua_wiki_content_for_compilation = ["這是本王易經標題維基資料下載\n"]
    for i, gua_title in enumerate(gua_titles):
        print(f"Processing Gua {i+1}/{len(gua_titles)}: {gua_title}")
        raw_gua_path = os.path.join(YIJING_WIKI_GUA_RAW_PATH, f"yijing卦名維基文獻粗1第{i+1}條{gua_title}.txt")
        cleaned_gua_path = os.path.join(YIJING_WIKI_GUA_CLEANED_PATH, f"yijing卦名維基文獻第{i+1}條{gua_title}粗掃.txt")
        raw_text = get_wiki_content_basic(gua_title, raw_save_path=raw_gua_path, cleaned_save_path=cleaned_gua_path)
        if raw_text:
            all_gua_wiki_content_for_compilation.append(f"這是本王的資料---{gua_title}---\n{raw_text}\n")
        else:
            all_gua_wiki_content_for_compilation.append(f"這是本王的資料---{gua_title}---\nFailed to retrieve content.\n")
    with open(output_literature_file, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(all_gua_wiki_content_for_compilation))
    print(f"Successfully generated {output_literature_file}")
    with open(MAIN_COMPILATION_FILE, "a", encoding="utf-8") as f_main_comp:
        f_main_comp.write("\n以下是易經卦名維基文獻\n\n" + "\n".join(all_gua_wiki_content_for_compilation) + "\n")
    print(f"Appended Yijing Gua wiki content to {MAIN_COMPILATION_FILE}")

