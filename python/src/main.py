import sys
import os
import shutil
import re
import requests
import html2text
import traceback
from flask import Flask, render_template, jsonify, redirect, url_for, flash, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # DON'T CHANGE THIS !!!

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.secret_key = "supersecretkey_dev_only"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAD_DIR = "/home/ubuntu/dad"
WORK_DIR = os.path.join(APP_DIR, "work_dir")
APP_CONFIG_DIR = os.path.join(APP_DIR, "app_config")
APP_CONFIG_TEMPLATES_HTML_DIR = os.path.join(APP_CONFIG_DIR, "templates", "html_templates")
APP_CONFIG_TEMPLATES_SLIDES_DIR = os.path.join(APP_CONFIG_DIR, "templates", "slide_templates")
APP_CONFIG_SETTINGS_DIR = os.path.join(APP_CONFIG_DIR, "settings")

def copy_dir_robust(src, dst, symlinks=False, ignore=None):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=symlinks, ignore=ignore)

def ensure_empty_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path, exist_ok=True)

def ensure_dir_exists(dir_path):
    os.makedirs(dir_path, exist_ok=True)

# Function to copy individual files, creating parent directory if needed
def copy_file_robust(src_file, dst_file):
    try:
        ensure_dir_exists(os.path.dirname(dst_file))
        shutil.copy2(src_file, dst_file)
        return True, f"成功複製檔案：{os.path.basename(src_file)} 至 {dst_file}"
    except Exception as e:
        return False, f"複製檔案 {os.path.basename(src_file)} 失敗：{str(e)}"

@app.route('/')
def index():
    initialized = os.path.exists(os.path.join(WORK_DIR, "工具程式資料夾現在要用"))
    processed_yijing_ancient_text_file = os.path.join(WORK_DIR, "易經古原文暫存戰果資料夾", "yijing每卦到空列分隔全文文本有分斷點.txt")
    yijing_processed = os.path.exists(processed_yijing_ancient_text_file)
    html_generated_dir = os.path.join(WORK_DIR, "易經HTML暫存戰果資料夾")
    html_files_exist = os.path.exists(html_generated_dir) and len(os.listdir(html_generated_dir)) > 0
    slides_dir1 = os.path.join(WORK_DIR, "易經投影片暫存戰果資料夾")
    slides1_exist = os.path.exists(slides_dir1) and any(f.startswith("易經古文解析第") for f in os.listdir(slides_dir1))
    slides2_exist = os.path.exists(slides_dir1) and any(f.startswith("媽傳記與易經整合第") for f in os.listdir(slides_dir1))
    
    garbage_text_path = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字.txt")
    garbage_text_again_path = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字再一次.txt")
    
    garbage_text_content = ""
    if os.path.exists(garbage_text_path):
        with open(garbage_text_path, 'r', encoding='utf-8') as f:
            garbage_text_content = f.read()
            
    garbage_text_again_content = ""
    if os.path.exists(garbage_text_again_path):
        with open(garbage_text_again_path, 'r', encoding='utf-8') as f:
            garbage_text_again_content = f.read()

    return render_template('index.html', title='易經與媽傳記應用程式',
                           initialized=initialized, 
                           yijing_processed=yijing_processed, 
                           html_files_exist=html_files_exist,
                           slides1_exist=slides1_exist,
                           slides2_exist=slides2_exist,
                           garbage_text_content=garbage_text_content,
                           garbage_text_again_content=garbage_text_again_content)

@app.route('/initialize_data', methods=['POST'])
def initialize_data():
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        flash_messages = []

        # --- Phase 1: Initial copy from DAD_DIR and cleanup ---
        flash_messages.append(("開始階段一：從原始資料目錄複製並清理工作目錄...", "info"))
        dirs_to_copy_from_dad = {
            "工具程式資料夾": "工具程式資料夾現在要用",
            "基本資料資料夾": "基本資料資料夾現在要用",
            "HTML參考樣板資料夾": "HTML參考樣板資料夾現在要用", # Will be overwritten by app_config if exists
            "投影片參考樣板資料夾": "投影片參考樣板資料夾現在要用", # Will be overwritten by app_config if exists
            "易經輸入端資料夾": "易經輸入端資料夾現在要用"
        }
        for src_name, dst_name in dirs_to_copy_from_dad.items():
            src_path = os.path.join(DAD_DIR, src_name)
            dst_path = os.path.join(WORK_DIR, dst_name)
            if os.path.exists(src_path):
                copy_dir_robust(src_path, dst_path)
                flash_messages.append((f"成功從 DAD_DIR 複製資料夾：{src_name} 至 {dst_name}", "success"))
            else:
                ensure_dir_exists(dst_path) 
                flash_messages.append((f"警告：原始來源資料夾 {src_path} 不存在。已建立空目標資料夾 {dst_name}。", "warning"))

        m_txt_src = os.path.join(DAD_DIR, "m.txt")
        m_txt_dst = os.path.join(WORK_DIR, "m.txt")
        if os.path.exists(m_txt_src):
            shutil.copy2(m_txt_src, m_txt_dst)
            flash_messages.append(("成功從 DAD_DIR 複製檔案：m.txt", "success"))
        else:
            flash_messages.append((f"警告：原始來源檔案 {m_txt_src} 不存在。", "warning"))

        base_data_dir = os.path.join(WORK_DIR, "基本資料資料夾現在要用")
        if os.path.exists(base_data_dir):
            processed_files_count = 0
            for filename in os.listdir(base_data_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(base_data_dir, filename)
                    formatted_file_name = f"{os.path.splitext(filename)[0]}格式化.txt"
                    formatted_file_path = os.path.join(base_data_dir, formatted_file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            lines = infile.readlines()
                        with open(formatted_file_path, 'w', encoding='utf-8') as outfile:
                            for line_content in lines:
                                modified_line_content = re.sub(r"(.{2,})(  )(.{2,})", r"\1 &nbsp; \3", line_content.rstrip("\r\n"), 1)
                                outfile.write(modified_line_content + "\n")
                        processed_files_count += 1
                    except Exception as e:
                        flash_messages.append((f"處理檔案 {filename} 時發生錯誤：{str(e)}", "error"))
            if processed_files_count > 0:
                 flash_messages.append((f"成功格式化 {processed_files_count} 個文字檔案。", "success"))
        else:
            flash_messages.append((f"警告：資料夾 {base_data_dir} 不存在，無法格式化文字檔案。", "warning"))

        dir_groups = {
            "main_results": ["易經總戰果", "易經總戰果1", "易經總戰果2", "易經戰果", "易經中間成品", "易經標記"],
            "wiki_temp": [f"易經維基網資料暫存{i}" for i in range(1, 13)] + ["易經維基網資料暫存戰果"],
            "ancient_text_temp": [f"易經古原文暫存{i}" for i in range(1, 6)] + ["易經古原文暫存戰果"],
            "html_temp": [f"易經HTML暫存{i}" for i in range(1, 6)] + ["易經HTML暫存戰果"],
            "slides_temp": [f"易經投影片暫存{i}" for i in range(1, 13)] + ["易經投影片暫存戰果"]
        }
        created_dirs_count = 0
        for group_key, dir_list in dir_groups.items():
            for dir_name_base in dir_list:
                ensure_empty_dir(os.path.join(WORK_DIR, f"{dir_name_base}資料夾"))
                created_dirs_count += 1
        if created_dirs_count > 0:
            flash_messages.append((f"成功建立/清理 {created_dirs_count} 個暫存資料夾。", "success"))

        flash_messages.append(("開始階段二：從永久設定目錄還原樣板與設定...", "info"))
        
        html_templates_work_dir = os.path.join(WORK_DIR, "HTML參考樣板資料夾現在要用")
        ensure_dir_exists(html_templates_work_dir)
        if os.path.exists(APP_CONFIG_TEMPLATES_HTML_DIR):
            for item_name in os.listdir(APP_CONFIG_TEMPLATES_HTML_DIR):
                src_item_path = os.path.join(APP_CONFIG_TEMPLATES_HTML_DIR, item_name)
                dst_item_path = os.path.join(html_templates_work_dir, item_name)
                if os.path.isfile(src_item_path):
                    success, msg = copy_file_robust(src_item_path, dst_item_path)
                    flash_messages.append((msg, "success" if success else "error"))
                elif os.path.isdir(src_item_path):
                    copy_dir_robust(src_item_path, dst_item_path)
                    flash_messages.append((f"成功從 APP_CONFIG 還原HTML樣板資料夾：{item_name}", "success"))
            flash_messages.append(("HTML 樣板還原完成。", "info"))
        else:
            flash_messages.append((f"警告：永久HTML樣板目錄 {APP_CONFIG_TEMPLATES_HTML_DIR} 不存在。", "warning"))

        slide_templates_work_dir = os.path.join(WORK_DIR, "投影片參考樣板資料夾現在要用")
        ensure_dir_exists(slide_templates_work_dir)
        if os.path.exists(APP_CONFIG_TEMPLATES_SLIDES_DIR):
            for item_name in os.listdir(APP_CONFIG_TEMPLATES_SLIDES_DIR):
                src_item_path = os.path.join(APP_CONFIG_TEMPLATES_SLIDES_DIR, item_name)
                dst_item_path = os.path.join(slide_templates_work_dir, item_name)
                if os.path.isfile(src_item_path):
                    success, msg = copy_file_robust(src_item_path, dst_item_path)
                    flash_messages.append((msg, "success" if success else "error"))
                elif os.path.isdir(src_item_path):
                    copy_dir_robust(src_item_path, dst_item_path)
                    flash_messages.append((f"成功從 APP_CONFIG 還原投影片樣板資料夾：{item_name}", "success"))
            flash_messages.append(("投影片樣板還原完成。", "info"))
        else:
            flash_messages.append((f"警告：永久投影片樣板目錄 {APP_CONFIG_TEMPLATES_SLIDES_DIR} 不存在。", "warning"))

        garbage_settings_work_dir = os.path.join(WORK_DIR, "工具程式資料夾現在要用")
        ensure_dir_exists(garbage_settings_work_dir)
        garbage_files_to_restore = ["掃垃圾文字.txt", "掃垃圾文字再一次.txt"]
        if os.path.exists(APP_CONFIG_SETTINGS_DIR):
            for filename in garbage_files_to_restore:
                src_file = os.path.join(APP_CONFIG_SETTINGS_DIR, filename)
                dst_file = os.path.join(garbage_settings_work_dir, filename)
                if os.path.exists(src_file):
                    success, msg = copy_file_robust(src_file, dst_file)
                    flash_messages.append((msg, "success" if success else "error"))
                else:
                    if not os.path.exists(dst_file):
                        with open(dst_file, 'w', encoding='utf-8') as f_empty:
                            f_empty.write("")
                        flash_messages.append((f"警告：垃圾詞彙檔案 {filename} 在 APP_CONFIG 和 DAD_DIR 中均未找到，已在工作目錄建立空檔案。", "warning"))
                    else:
                        flash_messages.append((f"提示：垃圾詞彙檔案 {filename} 未在 APP_CONFIG 中找到，將使用 DAD_DIR 版本 (如果存在)。", "info"))
            flash_messages.append(("垃圾詞彙設定還原完成。", "info"))
        else:
            flash_messages.append((f"警告：永久設定目錄 {APP_CONFIG_SETTINGS_DIR} 不存在。將依賴 DAD_DIR 版本或建立空檔案。", "warning"))
            for filename in garbage_files_to_restore:
                dst_file = os.path.join(garbage_settings_work_dir, filename)
                if not os.path.exists(dst_file):
                    with open(dst_file, 'w', encoding='utf-8') as f_empty:
                        f_empty.write("")
                    flash_messages.append((f"已在工作目錄為 {filename} 建立空檔案。", "info"))

        for msg, cat in flash_messages:
            flash(msg, cat)
        if not any(cat == 'error' for _, cat in flash_messages):
             flash("資料初始化與設定還原成功完成！", "success")
        else:
            flash("資料初始化或設定還原過程中發生錯誤，請檢查訊息。", "error")
            
    except Exception as e:
        flash(f"資料初始化失敗：{str(e)}", "error")
        traceback.print_exc()
    
    return redirect(url_for('index'))

@app.route('/save_garbage_lists', methods=['POST'])
def save_garbage_lists():
    try:
        garbage_text = request.form.get('garbage_text_content', '')
        garbage_text_again = request.form.get('garbage_text_again_content', '')

        ensure_dir_exists(APP_CONFIG_SETTINGS_DIR)
        ensure_dir_exists(os.path.join(WORK_DIR, "工具程式資料夾現在要用"))

        app_config_garbage_path = os.path.join(APP_CONFIG_SETTINGS_DIR, "掃垃圾文字.txt")
        app_config_garbage_again_path = os.path.join(APP_CONFIG_SETTINGS_DIR, "掃垃圾文字再一次.txt")
        
        work_dir_garbage_path = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字.txt")
        work_dir_garbage_again_path = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字再一次.txt")

        with open(app_config_garbage_path, 'w', encoding='utf-8') as f:
            f.write(garbage_text)
        with open(work_dir_garbage_path, 'w', encoding='utf-8') as f:
            f.write(garbage_text)
            
        with open(app_config_garbage_again_path, 'w', encoding='utf-8') as f:
            f.write(garbage_text_again)
        with open(work_dir_garbage_again_path, 'w', encoding='utf-8') as f:
            f.write(garbage_text_again)
            
        flash("垃圾詞彙列表已成功儲存！", "success")
    except Exception as e:
        flash(f"儲存垃圾詞彙列表失敗：{str(e)}", "error")
        traceback.print_exc()
    return redirect(url_for('index'))


@app.route('/download_wiki_data', methods=['POST'])
def download_wiki_data():
    if not os.path.exists(os.path.join(WORK_DIR, "工具程式資料夾現在要用")) or \
       not os.path.exists(os.path.join(WORK_DIR, "易經輸入端資料夾現在要用")):
        flash("錯誤：請先執行資料初始化。", "error")
        return redirect(url_for('index'))

    try:
        start_line = int(request.form.get('start_line_wiki', 1))
        end_line = int(request.form.get('end_line_wiki', 1))
        flash_messages = []

        yijing_terms_file = os.path.join(WORK_DIR, "易經輸入端資料夾現在要用", "易經自選專有名詞.txt")
        garbage_terms_file = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字.txt")
        garbage_again_terms_file = os.path.join(WORK_DIR, "工具程式資料夾現在要用", "掃垃圾文字再一次.txt")

        output_dir_base = os.path.join(WORK_DIR, "易經維基網資料暫存")
        output_dir_final_agg = os.path.join(WORK_DIR, "易經維基網資料暫存戰果資料夾")
        
        for i in range(1, 6):
            ensure_empty_dir(os.path.join(output_dir_base + f"{i}資料夾"))
        ensure_empty_dir(output_dir_final_agg)

        if not os.path.exists(yijing_terms_file):
            flash(f"錯誤：易經自選專有名詞檔案不存在 ({yijing_terms_file})", "error")
            return redirect(url_for('index'))
        if not os.path.exists(garbage_terms_file):
            flash(f"錯誤：掃垃圾文字檔案不存在 ({garbage_terms_file})。請嘗試重新初始化或檢查設定。", "error")
            return redirect(url_for('index'))
        if not os.path.exists(garbage_again_terms_file):
            flash(f"錯誤：掃垃圾文字再一次檔案不存在 ({garbage_again_terms_file})。請嘗試重新初始化或檢查設定。", "error")
            return redirect(url_for('index'))

        with open(yijing_terms_file, 'r', encoding='utf-8') as f:
            all_terms = [line.strip() for line in f if line.strip()]
        
        selected_terms = all_terms[start_line-1:end_line]

        if not selected_terms:
            flash("警告：根據所選行號，沒有選中任何專有名詞。", "warning")
            return redirect(url_for('index'))

        with open(garbage_terms_file, 'r', encoding='utf-8') as f:
            garbage_list = [line.strip() for line in f if line.strip()]
        with open(garbage_again_terms_file, 'r', encoding='utf-8') as f:
            garbage_again_list = [line.strip() for line in f if line.strip()]

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True

        final_wiki_content_path = os.path.join(output_dir_final_agg, "自選專有名詞維基文獻.txt")
        with open(final_wiki_content_path, 'w', encoding='utf-8') as f_agg:
            f_agg.write("這是本王自選標題維基資料下載\n\n")

        for i, term in enumerate(selected_terms):
            term_index_in_script = start_line + i
            flash_messages.append((f"開始處理專有名詞：{term} ({i+1}/{len(selected_terms)})", "info"))

            wiki_url = f"http://zh.wikipedia.org/zh-tw/{term}"
            text_content_path_step1 = os.path.join(output_dir_base + "1資料夾", f"自選專有名詞維基文獻粗1第{term_index_in_script}條.txt")
            
            try:
                response = requests.get(wiki_url, timeout=15)
                response.raise_for_status()
                raw_html = response.text
                text_content_step1 = h.handle(raw_html)
                with open(text_content_p
(Content truncated due to size limit. Use line ranges to read in chunks)