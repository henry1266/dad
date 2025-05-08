# -*- coding: utf-8 -*-
import os

# 設定固定資料夾路徑
BASH_SOURCE_DIR = "/home/ubuntu/dad/bash"
CONFIG_DATA_PATH = "/home/ubuntu/dad/config_data"

# 輸入資料路徑
YIJING_INPUT_PATH = os.path.join(CONFIG_DATA_PATH, "易經輸入端資料夾")
BASIC_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "基本資料資料夾")
TOOL_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "工具程式資料夾")
HTML_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "HTML參考樣板資料夾")
SLIDES_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "投影片參考樣板資料夾")
M_TXT_PATH = os.path.join(CONFIG_DATA_PATH, "m.txt")
FENGSHUI_CASES_PATH = os.path.join(CONFIG_DATA_PATH, "易經個案資料夾")

# 生成內容的資料夾路徑
YIJING_TOTAL_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經總戰果資料夾")
YIJING_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經戰果資料夾")
YIJING_INTERMEDIATE_PATH = os.path.join(CONFIG_DATA_PATH, "易經中間成品質料夾")
YIJING_MARKING_PATH = os.path.join(CONFIG_DATA_PATH, "易經標記資料夾")
YIJING_ANCIENT_TEXT_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存戰果資料夾") # Store split ancient texts
YIJING_WIKI_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存戰果資料夾")
YIJING_HTML_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存戰果資料夾")
YIJING_SLIDES_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存戰果資料夾")

# 暫存檔案的父資料夾路徑
YIJING_WIKI_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存資料夾")
YIJING_ANCIENT_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存資料夾") # Temp for raw yijing.txt processing
YIJING_HTML_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存資料夾")
YIJING_SLIDES_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存資料夾")

# 64卦維基百科結果的特定子目錄
YIJING_WIKI_GUA_RAW_PATH = os.path.join(YIJING_WIKI_TEMP_PATH, "1") # 易經維基網資料暫存1資料夾
YIJING_WIKI_GUA_CLEANED_PATH = os.path.join(YIJING_WIKI_TEMP_PATH, "5") # 易經維基網資料暫存5資料夾

# 主要彙編檔案
MAIN_COMPILATION_FILE = os.path.join(YIJING_TOTAL_RESULT_PATH, "我的著作文獻部份.txt")

