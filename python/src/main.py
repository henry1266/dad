# -*- coding: utf-8 -*-
"""Flask application factory for the DAD Yijing web interface."""
from __future__ import annotations

from dataclasses import asdict
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
from .config import YIJING_ANCIENT_TEXT_PATH
from .content_catalog import build_content_catalog
from .page_generator import fengshui_bp, gua_bp
from .processing import ProcessingSelection, ProcessingStepResult, run_processing
from .slide_generator import slides_bp


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


def _processing_selection_from_request() -> ProcessingSelection:
    start = _parse_form_int("custom_topic_start", 1)
    end = _parse_form_int("custom_topic_end", 1)
    validate_range(start, end, minimum=1, maximum=10_000, max_span=50)
    return ProcessingSelection(
        run_prepare_env=request.form.get("run_prepare_environment") == "true",
        run_format_basic=request.form.get("run_format_basic_data") == "true",
        run_process_raw=request.form.get("run_process_yijing_raw") == "true",
        run_gen_meta=request.form.get("run_generate_yijing_meta") == "true",
        run_append_ancient=request.form.get("run_append_ancient_texts") == "true",
        run_custom_wiki=request.form.get("run_process_custom_wiki") == "true",
        run_guas_wiki=request.form.get("run_process_guas_wiki") == "true",
        custom_topic_start=start,
        custom_topic_end=end,
    )


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

    @app.errorhandler(404)
    def not_found(_error):
        return (
            render_template(
                "error.html",
                error_code=404,
                error_title="找不到內容",
                error_message="這筆內容不存在、尚未準備完成，或已不在目錄中。",
            ),
            404,
        )

    @app.before_request
    def protect_state_changing_requests() -> None:
        if request.url_rule is None or request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        expected = session.get("_csrf_token")
        submitted = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        if not expected or not submitted or not hmac.compare_digest(str(expected), str(submitted)):
            abort(400, description="CSRF token validation failed")

    @app.get("/")
    def index():
        catalog = build_content_catalog()
        return render_template(
            "index.html",
            catalog=catalog,
            gua_entries=catalog.entries_for("gua"),
            slide_entries=catalog.entries_for("slides"),
            case_entries=catalog.entries_for("fengshui_case"),
            catalog_warnings=catalog.warnings,
        )

    @app.get("/workspace")
    def workspace():
        flashed = get_flashed_messages(category_filter=["processing_report"])
        return render_template(
            "workspace.html",
            processing_results=flashed[-1] if flashed else [],
        )

    @app.post("/workspace/process")
    def process_workspace():
        try:
            results = run_processing(_processing_selection_from_request())
        except ValueError as exc:
            results = (
                ProcessingStepResult("輸入驗證", "error", f"輸入資料有誤：{exc}"),
            )
        flash([asdict(result) for result in results], "processing_report")
        return redirect(url_for("workspace"))

    if env_flag("DAD_AUTO_INITIALIZE", False):
        with app.app_context():
            try:
                if not os.path.isdir(YIJING_ANCIENT_TEXT_PATH) or not os.listdir(
                    YIJING_ANCIENT_TEXT_PATH
                ):
                    run_processing(
                        ProcessingSelection(
                            run_prepare_env=True,
                            run_format_basic=True,
                            run_process_raw=True,
                            run_gen_meta=True,
                            run_append_ancient=True,
                        )
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
