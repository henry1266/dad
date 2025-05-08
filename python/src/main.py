# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, url_for, request, redirect, flash

# Import functionalities from refactored modules
from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH, FENGSHUI_CASES_PATH
from .data_processor import (
    prepare_environment,
    format_basic_data_files,
    process_yijing_raw_text,
    generate_yijing_metadata_and_split_guas,
    append_ancient_texts_to_compilation
)
from .wiki_handler import (
    process_custom_topics_wiki,
    process_yijing_guas_wiki
)
from .slide_generator import slides_bp
from .page_generator import gua_bp, fengshui_bp

def initialize_all_data(run_prepare_env=True, run_format_basic=True, 
                        run_process_raw=True, run_gen_meta=True, 
                        run_append_ancient=True, run_custom_wiki=True, 
                        run_guas_wiki=True, custom_topic_start=1, custom_topic_end=1):
    """Runs selected data initialization and processing steps."""
    print("Running selected data processing...")
    message_log = []

    if run_prepare_env:
        print("Executing: prepare_environment")
        prepare_environment()
        message_log.append("環境準備完成。")
    
    if run_format_basic:
        print("Executing: format_basic_data_files")
        format_basic_data_files()
        message_log.append("基本資料檔案格式化完成。")

    yijing_processed = False
    if run_process_raw:
        print("Executing: process_yijing_raw_text")
        if process_yijing_raw_text():
            message_log.append("易經原始文字檔處理完成。")
            yijing_processed = True
        else:
            message_log.append("易經原始文字檔處理失敗。")
    
    metadata_generated = False
    if run_gen_meta:
        if yijing_processed or os.path.exists(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing每卦到空列分隔全文文本有分斷點.txt")):
            print("Executing: generate_yijing_metadata_and_split_guas")
            if generate_yijing_metadata_and_split_guas():
                message_log.append("易經元數據產生並分割卦文完成。")
                metadata_generated = True
            else:
                message_log.append("易經元數據產生並分割卦文失敗。")
        else:
            message_log.append("未執行易經元數據產生，因原始文字檔未處理或不存在。")

    if run_append_ancient:
        if metadata_generated or os.path.exists(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")):
            print("Executing: append_ancient_texts_to_compilation")
            append_ancient_texts_to_compilation()
            message_log.append("易經古文附加到彙編完成。")
        else:
            message_log.append("未執行易經古文附加到彙編，因元數據未產生或不存在。")

    if run_custom_wiki:
        print(f"Executing: process_custom_topics_wiki (lines {custom_topic_start}-{custom_topic_end})")
        process_custom_topics_wiki(begin_line=custom_topic_start, end_line=custom_topic_end)
        message_log.append(f"自選主題維基百科資料處理完成 (行 {custom_topic_start}-{custom_topic_end})。")

    if run_guas_wiki:
        # This function doesn't take start/end gua, it processes all 64 based on yijing標題.txt
        # The form fields start_gua/end_gua are not directly used by this specific function call
        # but could be used for other features in the future (e.g. generating only a range of HTML pages)
        print("Executing: process_yijing_guas_wiki")
        process_yijing_guas_wiki()
        message_log.append("易經64卦維基百科資料處理完成。")
    
    print("Selected data processing complete.")
    return "\n".join(message_log)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = "your_very_secret_key_for_flashing_messages" # Needed for flash()

    app.register_blueprint(slides_bp, url_prefix="/slides")
    app.register_blueprint(gua_bp, url_prefix="/gua")
    app.register_blueprint(fengshui_bp, url_prefix="/fengshui")

    @app.route("/", methods=["GET"])
    def index():
        interaction_message = flash("interaction_message") # Get flashed message
        if interaction_message:
            interaction_message = interaction_message[0]
            
        slide_shows = [
            {"url": url_for("slides.yijing_slides_lecture_ancient"), "title": "易經古文解析講座 (全文)"},
            {"url": url_for("slides.yijing_slides_lecture_guaci_moms_records"), "title": "易經卦駁段與媽傳記講座"},
            {"url": url_for("slides.yijing_slides_lecture_tuanxiang"), "title": "易經彖象解析講座"}
        ]
        gua_page_links = []
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if os.path.exists(titles_path):
            with open(titles_path, "r", encoding="utf-8") as f:
                all_titles = [line.strip() for line in f if line.strip()]
            # The form start_gua/end_gua are for data processing, not for limiting display here yet.
            # For now, display all available gua links.
            for i in range(len(all_titles)):
                gua_page_links.append({
                    "url": url_for("gua.gua_page", gua_number=i+1),
                    "title": f"第{i+1}卦 {all_titles[i]}"
                })
        else:
            print(f"Warning: Yijing titles file not found at {titles_path}, Gua links will be missing.")

        fengshui_case_links = []
        case_list_file = os.path.join(YIJING_INPUT_PATH, "易經個案列表.txt")
        if os.path.exists(case_list_file):
            with open(case_list_file, "r", encoding="utf-8") as f:
                case_files = [line.strip() for line in f if line.strip()]
            for case_file_base in case_files:
                fengshui_case_links.append({
                    "url": url_for("fengshui.fengshui_case_page", case_filename=case_file_base),
                    "title": f"風水個案：{case_file_base}" 
                })
        else:
            print(f"Warning: Fengshui case list file not found at {case_list_file}, Fengshui links will be missing.")

        return render_template("index.html", 
                               title="易經互動網頁", 
                               slide_shows=slide_shows, 
                               gua_pages=gua_page_links,
                               fengshui_cases=fengshui_case_links,
                               interaction_message=interaction_message)

    @app.route("/process_interaction", methods=["POST"])
    def process_interaction_route():
        try:
            # start_gua = int(request.form.get("start_gua", 1))
            # end_gua = int(request.form.get("end_gua", 64))
            custom_topic_start = int(request.form.get("custom_topic_start", 1))
            custom_topic_end = int(request.form.get("custom_topic_end", 1))

            run_prepare_env = request.form.get("run_prepare_environment") == "true"
            run_format_basic = request.form.get("run_format_basic_data") == "true"
            run_process_raw = request.form.get("run_process_yijing_raw") == "true"
            run_gen_meta = request.form.get("run_generate_yijing_meta") == "true"
            run_append_ancient = request.form.get("run_append_ancient_texts") == "true"
            run_custom_wiki = request.form.get("run_process_custom_wiki") == "true"
            run_guas_wiki = request.form.get("run_process_guas_wiki") == "true"
            generate_all = request.form.get("generate_all_outputs") == "true"

            messages = []
            if generate_all:
                # This re-runs all data processing, which implicitly updates files for pages/slides
                messages.append(initialize_all_data(custom_topic_start=custom_topic_start, custom_topic_end=custom_topic_end))
                messages.append("已觸發所有資料重新處理與生成。網頁和投影片將使用最新資料。")
            else:
                # Run specific selected functions
                messages.append(initialize_all_data(
                    run_prepare_env=run_prepare_env,
                    run_format_basic=run_format_basic,
                    run_process_raw=run_process_raw,
                    run_gen_meta=run_gen_meta,
                    run_append_ancient=run_append_ancient,
                    run_custom_wiki=run_custom_wiki,
                    run_guas_wiki=run_guas_wiki,
                    custom_topic_start=custom_topic_start,
                    custom_topic_end=custom_topic_end
                ))
            
            flash("\n".join(messages), "interaction_message")
        except Exception as e:
            flash(f"處理請求時發生錯誤: {str(e)}", "interaction_message")
            print(f"Error in /process_interaction: {e}")
            import traceback
            traceback.print_exc()
        return redirect(url_for("index"))

    # Run initial data processing once on startup if no specific interaction is triggered first.
    # This ensures the app has some data to show on first load.
    # However, the form now allows users to trigger this, so we might make it optional on startup.
    # For now, let it run to populate links.
    with app.app_context():
        # Simplified initial call, user can re-run specifics via form
        print("Performing a minimal data check/setup on startup...")
        if not os.path.exists(YIJING_ANCIENT_TEXT_PATH) or not os.listdir(YIJING_ANCIENT_TEXT_PATH):
             initialize_all_data(run_custom_wiki=False, run_guas_wiki=False) # Run core Yijing processing
        else:
            print("Core data seems to exist. Skipping full initial processing.")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)

