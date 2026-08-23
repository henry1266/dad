# -*- coding: utf-8 -*-
"""Flask application factory for the DAD Yijing web interface."""
from __future__ import annotations

import hmac
import os
import secrets
from typing import Any

from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .app_support import env_flag, validate_range
from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH
from .data_processor import (
    append_ancient_texts_to_compilation,
    format_basic_data_files,
    generate_yijing_metadata_and_split_guas,
    prepare_environment,
    process_yijing_raw_text,
)
from .page_generator import fengshui_bp, gua_bp
from .slide_generator import slides_bp
from .wiki_handler import process_custom_topics_wiki, process_yijing_guas_wiki


def initialize_all_data(
    *,
    run_prepare_env: bool = False,
    run_format_basic: bool = False,
    run_process_raw: bool = False,
    run_gen_meta: bool = False,
    run_append_ancient: bool = False,
    run_custom_wiki: bool = False,
    run_guas_wiki: bool = False,
    custom_topic_start: int = 1,
    custom_topic_end: int = 1,
) -> str:
    """Run only the explicitly selected processing steps."""
    message_log: list[str] = []

    if run_prepare_env:
        prepare_environment(reset=False)
        message_log.append("環境準備完成，既有檔案已保留。")

    if run_format_basic:
        format_basic_data_files()
        message_log.append("基本資料檔案格式化完成。")

    yijing_processed = False
    if run_process_raw:
        yijing_processed = process_yijing_raw_text()
        message_log.append(
            "易經原始文字檔處理完成。" if yijing_processed else "易經原始文字檔處理失敗。"
        )

    metadata_generated = False
    if run_gen_meta:
        processed_path = os.path.join(
            YIJING_ANCIENT_TEXT_PATH,
            "yijing每卦到空列分隔全文文本有分斷點.txt",
        )
        if yijing_processed or os.path.exists(processed_path):
            metadata_generated = generate_yijing_metadata_and_split_guas()
            message_log.append(
                "易經元數據產生並分割卦文完成。"
                if metadata_generated
                else "易經元數據產生或分割卦文失敗。"
            )
        else:
            message_log.append("未產生易經元數據，因處理後的原始文字檔不存在。")

    if run_append_ancient:
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if metadata_generated or os.path.exists(titles_path):
            append_ancient_texts_to_compilation()
            message_log.append("易經古文已寫入彙編。")
        else:
            message_log.append("未寫入易經古文，因標題資料不存在。")

    if run_custom_wiki:
        succeeded = process_custom_topics_wiki(
            begin_line=custom_topic_start,
            end_line=custom_topic_end,
        )
        message_log.append(
            f"自選主題維基百科資料處理完成（第 {custom_topic_start} 至 {custom_topic_end} 行）。"
            if succeeded
            else "自選主題維基百科資料未完成，請查看伺服器紀錄。"
        )

    if run_guas_wiki:
        succeeded = process_yijing_guas_wiki()
        message_log.append(
            "易經卦名維基百科資料處理完成。"
            if succeeded
            else "易經卦名維基百科資料未完成，請查看伺服器紀錄。"
        )

    return "\n".join(message_log) if message_log else "未選擇任何操作。"


def _csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def _parse_form_int(name: str, default: int) -> int:
    raw_value = request.form.get(name, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"欄位 {name} 必須是整數。") from exc


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("DAD_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=env_flag("DAD_SESSION_COOKIE_SECURE", False),
    )
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(slides_bp, url_prefix="/slides")
    app.register_blueprint(gua_bp, url_prefix="/gua")
    app.register_blueprint(fengshui_bp, url_prefix="/fengshui")
    app.jinja_env.globals["csrf_token"] = _csrf_token

    @app.before_request
    def protect_state_changing_requests() -> None:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        expected = session.get("_csrf_token")
        submitted = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        if not expected or not submitted or not hmac.compare_digest(str(expected), str(submitted)):
            abort(400, description="CSRF token validation failed")

    @app.get("/")
    def index():
        flashed = get_flashed_messages(category_filter=["interaction_message"])
        interaction_message = flashed[-1] if flashed else None

        slide_shows = [
            {
                "url": url_for("slides.yijing_slides_lecture_ancient"),
                "title": "易經古文解析講座（全文）",
            },
            {
                "url": url_for("slides.yijing_slides_lecture_guaci_moms_records"),
                "title": "易經卦辭與媽傳記講座",
            },
            {
                "url": url_for("slides.yijing_slides_lecture_tuanxiang"),
                "title": "易經彖象解析講座",
            },
        ]

        gua_page_links: list[dict[str, str]] = []
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if os.path.isfile(titles_path):
            with open(titles_path, "r", encoding="utf-8") as handle:
                all_titles = [line.strip() for line in handle if line.strip()]
            gua_page_links = [
                {
                    "url": url_for("gua.gua_page", gua_number=index),
                    "title": f"第{index}卦 {title}",
                }
                for index, title in enumerate(all_titles, start=1)
            ]

        fengshui_case_links: list[dict[str, str]] = []
        case_list_file = os.path.join(YIJING_INPUT_PATH, "易經個案列表.txt")
        if os.path.isfile(case_list_file):
            with open(case_list_file, "r", encoding="utf-8") as handle:
                case_files = [line.strip() for line in handle if line.strip()]
            fengshui_case_links = [
                {
                    "url": url_for("fengshui.fengshui_case_page", case_filename=case_file),
                    "title": f"風水個案：{case_file.removesuffix('.txt')}",
                }
                for case_file in case_files
            ]

        return render_template(
            "index.html",
            title="易經互動網頁",
            slide_shows=slide_shows,
            gua_pages=gua_page_links,
            fengshui_cases=fengshui_case_links,
            interaction_message=interaction_message,
        )

    @app.post("/process_interaction")
    def process_interaction():
        try:
            custom_topic_start = _parse_form_int("custom_topic_start", 1)
            custom_topic_end = _parse_form_int("custom_topic_end", 1)
            validate_range(
                custom_topic_start,
                custom_topic_end,
                minimum=1,
                maximum=10_000,
                max_span=50,
            )

            selections = {
                "run_prepare_env": request.form.get("run_prepare_environment") == "true",
                "run_format_basic": request.form.get("run_format_basic_data") == "true",
                "run_process_raw": request.form.get("run_process_yijing_raw") == "true",
                "run_gen_meta": request.form.get("run_generate_yijing_meta") == "true",
                "run_append_ancient": request.form.get("run_append_ancient_texts") == "true",
                "run_custom_wiki": request.form.get("run_process_custom_wiki") == "true",
                "run_guas_wiki": request.form.get("run_process_guas_wiki") == "true",
            }
            if request.form.get("generate_all_outputs") == "true":
                selections = {key: True for key in selections}

            message = initialize_all_data(
                **selections,
                custom_topic_start=custom_topic_start,
                custom_topic_end=custom_topic_end,
            )
            flash(message, "interaction_message")
        except ValueError as exc:
            flash(f"輸入資料有誤：{exc}", "interaction_message")
        except Exception:
            app.logger.exception("Error while processing an interaction request")
            flash("處理請求時發生未預期錯誤，請查看伺服器紀錄。", "interaction_message")
        return redirect(url_for("index"))

    if env_flag("DAD_AUTO_INITIALIZE", False):
        with app.app_context():
            try:
                if not os.path.isdir(YIJING_ANCIENT_TEXT_PATH) or not os.listdir(
                    YIJING_ANCIENT_TEXT_PATH
                ):
                    initialize_all_data(
                        run_prepare_env=True,
                        run_format_basic=True,
                        run_process_raw=True,
                        run_gen_meta=True,
                        run_append_ancient=True,
                    )
            except OSError:
                app.logger.exception("Automatic initialization failed")

    return app


if __name__ == "__main__":
    application = create_app()
    try:
        port = int(os.environ.get("DAD_PORT", "5003"))
    except ValueError:
        port = 5003
    application.run(
        host=os.environ.get("DAD_HOST", "127.0.0.1"),
        port=port,
        debug=env_flag("DAD_DEBUG", False),
    )
