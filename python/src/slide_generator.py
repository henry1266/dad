# -*- coding: utf-8 -*-
import os
import glob
import traceback
from flask import Blueprint, render_template, url_for
from .config import (
    BASIC_DATA_PATH, YIJING_ANCIENT_TEXT_PATH, SLIDES_TEMPLATE_PATH
)

slides_bp = Blueprint("slides", __name__, template_folder="../templates", static_folder="../static") # Adjusted paths for blueprint

@slides_bp.route("/lecture_ancient")
def yijing_slides_lecture_ancient():
    slides_data = []
    error_message = None
    slide_x_offset = 0
    slide_y_offset = 0
    slide_idx = 0
    try:
        for i in range(1, 7):
            formatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*格式化.txt")
            actual_files = glob.glob(formatted_file_pattern)
            actual_file_to_read, base_name_part = None, ""
            if actual_files:
                actual_file_to_read = actual_files[0]
                base_name_part = os.path.basename(actual_file_to_read).replace("格式化.txt", "").split(".")[0][3:]
            else:
                unformatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*.txt")
                for pf in glob.glob(unformatted_file_pattern):
                    if not pf.endswith("格式化.txt"):
                        actual_file_to_read = pf
                        base_name_part = os.path.basename(actual_file_to_read).split(".")[0][3:]
                        break
            if not actual_file_to_read:
                 raise FileNotFoundError(f"No file matching {i:03d}*.txt or {i:03d}*格式化.txt found in {BASIC_DATA_PATH}.")
            slide_title_map = {
                "執行長學經歷": "竹文診所 - 執行長學經歷", "總顧問學經歷": "竹文診所 - 總顧問學經歷",
                "中藥局營業項目": "竹文診所 - 中藥局營業項目", "中藥局經營理念": "竹文診所 - 中藥局經營理念",
                "中藥局歷史源流": "竹文診所 - 中藥局歷史源流", "中藥局診療日記1090101": "竹文診所 - 中藥局診療日記"
            }
            current_slide_title = f"竹文診所 - {base_name_part}"
            for key_map, title_val in slide_title_map.items():
                if key_map.replace(" ", "") in base_name_part.replace(" ", ""):
                    current_slide_title = title_val; break
            with open(actual_file_to_read, "r", encoding="utf-8") as f:
                slides_data.append({
                    "title": current_slide_title, 
                    "content": f.read().replace("\n", "<br>"),
                    "data_x": slide_x_offset, "data_y": slide_y_offset, "data_z": 0, "type": "html_content"
                })
            slide_x_offset += 1200
            slide_idx += 1
    except FileNotFoundError as e:
        error_message = f"缺少基本資料檔案，無法產生部分投影片：{str(e)}。請確保相關檔案已放置於 {BASIC_DATA_PATH} 目錄下。"
    except Exception as e:
        error_message = (error_message + "\n" if error_message else "") + f"讀取基本資料投影片時發生錯誤: {str(e)}"
        traceback.print_exc()
    yijing_titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    titles = []
    if not os.path.exists(yijing_titles_path):
        error_message = (error_message + "\n" if error_message else "") + f"缺少易經標題檔案 ({yijing_titles_path})，無法產生易經卦文投影片。"
    else:
        try:
            with open(yijing_titles_path, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f if line.strip()]
            slide_y_offset_gua = slide_y_offset + 800 
            slide_x_offset_gua = 0
            for i_gua, title_name in enumerate(titles):
                gua_num = i_gua + 1
                gua_file_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_num}卦古原文無分斷點.txt")
                slide_content_html = f"<h3>易經古文共有64卦, 本段為第{gua_num}卦 {title_name}卦的條文</h3>"
                if os.path.exists(gua_file_path):
                    with open(gua_file_path, "r", encoding="utf-8") as gf:
                        gua_text_lines = [line.strip().replace("\\xxxx","").replace("\\xxx","").replace("\\xx","").replace("\\xxxxx","") for line in gf.readlines() if line.strip()]
                    slide_content_html += "<br>".join(gua_text_lines)
                    slides_data.append({
                        "title": f"易經古文解析 - 第{gua_num}卦 {title_name}", 
                        "content": slide_content_html,
                        "data_x": slide_x_offset_gua + (i_gua % 8) * 1200, 
                        "data_y": slide_y_offset_gua + (i_gua // 8) * 800,
                        "data_z": 0, "type": "html_content"
                    })
                else:
                    slides_data.append({
                        "title": f"易經古文解析 - 第{gua_num}卦 {title_name}", 
                        "content": f"缺少第{gua_num}卦 ({title_name}) 的古文檔案 ({gua_file_path})",
                        "data_x": slide_x_offset_gua + (i_gua % 8) * 1200,
                        "data_y": slide_y_offset_gua + (i_gua // 8) * 800,
                        "data_z": 0, "type": "html_content"
                    })
                slide_idx += 1
        except Exception as e:
            error_message = (error_message + "\n" if error_message else "") + f"讀取易經資料時發生錯誤: {str(e)}"
            traceback.print_exc()
    overview_x_val = 3500
    overview_y_val = 1500 + ( (len(titles) // 8) * 400 ) if titles else 1500
    overview_scale_val = 10 if slides_data else 1
    return render_template("slides_yijing_lecture.html", 
                           slides_data=slides_data, 
                           error_message=error_message, 
                           title="易經古文解析講座",
                           overview_x=overview_x_val,
                           overview_y=overview_y_val,
                           overview_scale=overview_scale_val)

@slides_bp.route("/lecture_guaci_moms_records")
def yijing_slides_lecture_guaci_moms_records():
    slides_data = []
    error_message = None
    slide_x = 0
    slide_y = 0
    slide_z = 0
    slide_idx = 0
    row_spacing = 800
    col_spacing = 1200
    def add_slide(title, content, type="html_content", image_url=None, video_url=None):
        nonlocal slide_x, slide_y, slide_idx
        slides_data.append({
            "title": title, "content": content, "type": type,
            "image_url": image_url, "video_url": video_url,
            "data_x": slide_x, "data_y": slide_y, "data_z": slide_z
        })
        slide_x += col_spacing
        slide_idx += 1
    def next_row():
        nonlocal slide_x, slide_y
        slide_x = 0
        slide_y += row_spacing
    try:
        add_slide("出版資訊", "<p>出版者：竹文出版社</p><p>發行者：竹文資訊</p><p>總經銷：竹文堂</p>")
        next_row()
        for i in range(1, 7):
            formatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*格式化.txt")
            actual_files = glob.glob(formatted_file_pattern)
            actual_file_to_read, base_name_part = None, ""
            if actual_files: 
                actual_file_to_read = actual_files[0]
                base_name_part = os.path.basename(actual_file_to_read).replace("格式化.txt", "").split(".")[0][3:]
            else: 
                unformatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*.txt")
                for pf in glob.glob(unformatted_file_pattern):
                    if not pf.endswith("格式化.txt"): 
                        actual_file_to_read = pf
                        base_name_part = os.path.basename(actual_file_to_read).split(".")[0][3:]
                        break
            if actual_file_to_read:
                slide_title_map = {
                    "執行長學經歷": "竹文診所 - 執行長學經歷", "總顧問學經歷": "竹文診所 - 總顧問學經歷",
                    "中藥局營業項目": "竹文診所 - 中藥局營業項目", "中藥局經營理念": "竹文診所 - 中藥局經營理念",
                    "中藥局歷史源流": "竹文診所 - 中藥局歷史源流", "中藥局診療日記1090101": "竹文診所 - 中藥局診療日記"
                }
                current_slide_title = f"竹文診所 - {base_name_part}"
                for key_map, title_val in slide_title_map.items():
                    if key_map.replace(" ", "") in base_name_part.replace(" ", ""): current_slide_title = title_val; break
                with open(actual_file_to_read, "r", encoding="utf-8") as f:
                    add_slide(current_slide_title, f.read().replace("\n", "<br>"))
            else: error_message = (error_message or "") + f"Missing basic data file for slide {i}\n"
        next_row()
        mom_notes_photos = sorted(glob.glob(os.path.join(SLIDES_TEMPLATE_PATH, "b[0-9]*.jpg")))
        for photo_path in mom_notes_photos:
            photo_filename = os.path.basename(photo_path)
            add_slide(f"媽手記相片 - {photo_filename}", "", type="image", image_url=url_for("slides.static", filename=f"slides_assets/{photo_filename}")) # Corrected static endpoint
        if mom_notes_photos: next_row()
        notepad_prog_file = os.path.join(SLIDES_TEMPLATE_PATH, "記事本程式.txt")
        if os.path.exists(notepad_prog_file):
            with open(notepad_prog_file, "r", encoding="utf-8") as f:
                add_slide("記事本摘要", f.read())
            next_row()
        else: print(f"Warning: {notepad_prog_file} not found.")
        mom_article_prog_file = os.path.join(SLIDES_TEMPLATE_PATH, "媽文章程式.txt")
        if os.path.exists(mom_article_prog_file):
            with open(mom_article_prog_file, "r", encoding="utf-8") as f:
                add_slide("媽文章", f.read())
            next_row()
        else: print(f"Warning: {mom_article_prog_file} not found.")
        life_photos = sorted(glob.glob(os.path.join(SLIDES_TEMPLATE_PATH, "c[0-9]*.jpg")))
        for photo_path in life_photos:
            photo_filename = os.path.basename(photo_path)
            add_slide(f"生活剪影 - {photo_filename}", "", type="image", image_url=url_for("slides.static", filename=f"slides_assets/{photo_filename}")) # Corrected static endpoint
        if life_photos: next_row()
        speech_prog_file = os.path.join(SLIDES_TEMPLATE_PATH, "我演講程式.txt")
        if os.path.exists(speech_prog_file):
            with open(speech_prog_file, "r", encoding="utf-8") as f:
                add_slide("演講紀錄", f.read())
            next_row()
        else: print(f"Warning: {speech_prog_file} not found.")
        palette_prog_file = os.path.join(SLIDES_TEMPLATE_PATH, "變色盤程式.txt")
        if os.path.exists(palette_prog_file):
            with open(palette_prog_file, "r", encoding="utf-8") as f:
                add_slide("變色盤參考", f.read())
            next_row()
        else: print(f"Warning: {palette_prog_file} not found.")
        yijing_titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if not os.path.exists(yijing_titles_path):
            error_message = (error_message or "") + f"Missing Yijing titles file: {yijing_titles_path}\n"
        else:
            with open(yijing_titles_path, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f if line.strip()]
            for i_gua, title_name in enumerate(titles):
                gua_num = i_gua + 1
                gua_file_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_num}卦古原文無分斷點.txt")
                if os.path.exists(gua_file_path):
                    with open(gua_file_path, "r", encoding="utf-8") as gf:
                        gua_lines = [line.strip() for line in gf.readlines() if line.strip()]
                    tuan_text, xiang_text = "", ""
                    in_tuan, in_xiang = False, False
                    for line in gua_lines:
                        if "\\xxxx" in line: in_tuan = True; continue
                        if "\\xxx" in line: in_xiang = True; in_tuan = False; continue
                        if "\\xx" in line or "\\xxxxx" in line : in_tuan = False; in_xiang = False; continue
                        if line.startswith("彖曰："): tuan_text += line.replace("彖曰：", "").strip() + "<br>"
                        elif line.startswith("象曰："): xiang_text += line.replace("象曰：", "").strip() + "<br>"
                        elif in_tuan and not line.startswith("《易經》"): tuan_text += line.strip() + "<br>"
                        elif in_xiang and not line.startswith("《易經》"): xiang_text += line.strip() + "<br>"
                    commentary_content = ""
                    if tuan_text: commentary_content += f"<h4>彖辭</h4><p>{tuan_text}</p>"
                    if xiang_text: commentary_content += f"<h4>象辭</h4><p>{xiang_text}</p>"
                    if commentary_content:
                        add_slide(f"易經卦解 - 第{gua_num}卦 {title_name} (彖/象)", commentary_content)
                    if (i_gua + 1) % 4 == 0 and (tuan_text or xiang_text): next_row()
                else: error_message = (error_message or "") + f"Missing gua file for {title_name}\n"
            if titles and len(titles) % 4 != 0 : next_row()
    except FileNotFoundError as e:
        error_message = (error_message or "") + f"檔案遺失錯誤 (媽傳記投影片): {str(e)}\n"
    except Exception as e:
        error_message = (error_message or "") + f"產生媽傳記投影片時發生錯誤: {str(e)}\n{traceback.format_exc()}"
    overview_x_val = (slide_idx // ((slide_y // row_spacing if slide_y > 0 else 0) +1 )) * col_spacing / 2 if slide_y > 0 and slide_idx > 0 else 3000
    overview_y_val = slide_y / 2 if slide_y > 0 else 1500
    overview_scale_val = 8 if slides_data else 1
    return render_template("slides_yijing_guaci_moms_records.html",
                           slides_data=slides_data, error_message=error_message,
                           title="易經卦駁段與媽傳記講座",
                           overview_x=overview_x_val, overview_y=overview_y_val, overview_scale=overview_scale_val)

@slides_bp.route("/lecture_tuanxiang")
def yijing_slides_lecture_tuanxiang():
    slides_data = []
    error_message = None
    slide_x = 0
    slide_y = 0
    slide_z = 0
    slide_idx = 0
    row_spacing = 800
    col_spacing = 1200
    def add_slide_tx(title, content):
        nonlocal slide_x, slide_y, slide_idx
        slides_data.append({
            "title": title, "content": content, "type": "html_content",
            "data_x": slide_x, "data_y": slide_y, "data_z": slide_z
        })
        slide_x += col_spacing
        if (slide_idx + 1) % 4 == 0:
            slide_x = 0
            slide_y += row_spacing
        slide_idx += 1
    try:
        yijing_titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if not os.path.exists(yijing_titles_path):
            raise FileNotFoundError(f"Missing Yijing titles file: {yijing_titles_path}")
        with open(yijing_titles_path, "r", encoding="utf-8") as f:
            titles = [line.strip() for line in f if line.strip()]
        for i_gua, title_name in enumerate(titles):
            gua_num = i_gua + 1
            gua_file_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_num}卦古原文無分斷點.txt")
            if not os.path.exists(gua_file_path):
                error_message = (error_message or "") + f"Missing gua file for {title_name}\n"
                continue
            with open(gua_file_path, "r", encoding="utf-8") as gf:
                gua_lines = [line.strip() for line in gf.readlines() if line.strip()]
            tuan_text, xiang_text = "", ""
            in_tuan, in_xiang = False, False
            current_section_text = ""
            for line in gua_lines:
                if "\\xxxx" in line :
                    in_tuan = True
                    in_xiang = False
                    current_section_text = ""
                    if line.startswith("彖曰："): current_section_text += line.replace("彖曰：","").strip()
                    continue
                elif "\\xxx" in line:
                    if tuan_text == "" and current_section_text: 
                        tuan_text = current_section_text.replace("\n", "<br>")
                    in_xiang = True
                    in_tuan = False
                    current_section_text = ""
                    if line.startswith("象曰："): current_section_text += line.replace("象曰：","").strip()
                    continue
                elif "\\xx" in line or "\\xxxxx" in line or line.startswith("《易經》"):
                    if in_tuan and current_section_text: tuan_text = current_section_text.replace("\n", "<br>")
                    if in_xiang and current_section_text: xiang_text = current_section_text.replace("\n", "<br>")
                    in_tuan, in_xiang = False, False
                    current_section_text = ""
                    if line.startswith("《易經》"): break 
                    continue
                if in_tuan:
                    current_section_text += "\n" + line if current_section_text else line
                elif in_xiang:
                    current_section_text += "\n" + line if current_section_text else line
            if in_tuan and current_section_text and not tuan_text: tuan_text = current_section_text.replace("\n", "<br>")
            if in_xiang and current_section_text and not xiang_text: xiang_text = current_section_text.replace("\n", "<br>")
            if tuan_text:
                add_slide_tx(f"{title_name} (第{gua_num}卦) - 彖辭", tuan_text)
            if xiang_text:
                add_slide_tx(f"{title_name} (第{gua_num}卦) - 象辭", xiang_text)
    except FileNotFoundError as e:
        error_message = (error_message or "") + f"檔案遺失錯誤 (彖象投影片): {str(e)}\n"
    except Exception as e:
        error_message = (error_message or "") + f"產生彖象投影片時發生錯誤: {str(e)}\n{traceback.format_exc()}"
    overview_x_val = (slide_idx // ((slide_y // row_spacing if slide_y > 0 else 0) +1 )) * col_spacing / 2 if slide_idx > 0 else 2000
    overview_y_val = slide_y / 2 if slide_y > 0 else 1000
    overview_scale_val = 6 if slides_data else 1
    return render_template("slides_yijing_tuanxiang.html", 
                           slides_data=slides_data, error_message=error_message, 
                           title="易經彖象解析講座",
                           overview_x=overview_x_val, overview_y=overview_y_val, overview_scale=overview_scale_val)

