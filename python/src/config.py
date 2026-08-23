# -*- coding: utf-8 -*-
"""Central path configuration for the DAD application.

Paths default to locations inside the repository and can be overridden with
environment variables. Keeping path construction in one module makes the app
portable across developer machines, CI and production hosts.
"""
from __future__ import annotations

import os
from pathlib import Path


def _resolved_path(value: str | os.PathLike[str]) -> str:
    return str(Path(value).expanduser().resolve())


_DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = _resolved_path(os.environ.get("DAD_PROJECT_ROOT", _DEFAULT_PROJECT_ROOT))
BASH_SOURCE_DIR = _resolved_path(
    os.environ.get("DAD_BASH_SOURCE_DIR", Path(PROJECT_ROOT) / "bash")
)
CONFIG_DATA_PATH = _resolved_path(
    os.environ.get("DAD_CONFIG_DATA_DIR", Path(PROJECT_ROOT) / "config_data")
)

# Input data paths
YIJING_INPUT_PATH = os.path.join(CONFIG_DATA_PATH, "易經輸入端資料夾")
BASIC_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "基本資料資料夾")
TOOL_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "工具程式資料夾")
HTML_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "HTML參考樣板資料夾")
SLIDES_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "投影片參考樣板資料夾")
M_TXT_PATH = os.path.join(CONFIG_DATA_PATH, "m.txt")

# Generated content paths
YIJING_TOTAL_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經總戰果資料夾")
YIJING_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經戰果資料夾")
YIJING_INTERMEDIATE_PATH = os.path.join(CONFIG_DATA_PATH, "易經中間成品質料夾")
YIJING_MARKING_PATH = os.path.join(CONFIG_DATA_PATH, "易經標記資料夾")
YIJING_ANCIENT_TEXT_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存戰果資料夾")
YIJING_WIKI_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存戰果資料夾")
YIJING_HTML_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存戰果資料夾")
YIJING_SLIDES_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存戰果資料夾")

# Temporary paths
YIJING_WIKI_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存資料夾")
YIJING_ANCIENT_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存資料夾")
YIJING_HTML_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存資料夾")
YIJING_SLIDES_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存資料夾")

YIJING_WIKI_GUA_RAW_PATH = os.path.join(YIJING_WIKI_TEMP_PATH, "1")
YIJING_WIKI_GUA_CLEANED_PATH = os.path.join(YIJING_WIKI_TEMP_PATH, "5")
MAIN_COMPILATION_FILE = os.path.join(YIJING_TOTAL_RESULT_PATH, "我的著作文獻部份.txt")
