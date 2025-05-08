# 初始化 Flask 應用程式
import sys
import os
from flask import Flask, render_template, Blueprint

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 設定固定資料夾路徑
CONFIG_DATA_PATH = "/home/ubuntu/dad/config_data"
YIJING_ANCIENT_TEXT_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存戰果資料夾")
YIJING_SLIDES_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存1資料夾")
BASIC_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "基本資料資料夾")

# # 如果需要資料庫，取消註解以下設定
# app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv("DB_USERNAME", "root")}:{os.getenv("DB_PASSWORD", "password")}@{os.getenv("DB_HOST", "localhost")}:{os.getenv("DB_PORT", "3306")}/{os.getenv("DB_NAME", "mydb")}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# # 初始化資料庫 (如果使用)
# from src.models import db
# db.init_app(app)

# 建立一個藍圖來組織易經相關的路由
yijing_bp = Blueprint('yijing', __name__, template_folder='templates')

@yijing_bp.route("/slides")
def yijing_slides_lecture():
    slides_data = []
    error_message = None

    # 讀取基本資料用於前幾張投影片 (模擬 bash 腳本的 ##<02-1> 部分)
    try:
        # 第1張: 執行長學經歷
        with open(os.path.join(BASIC_DATA_PATH, "001執行長學經歷格式化.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 執行長學經歷", "content": f.read().replace("\n", "<br>")})
        # 第2張: 總顧問學經歷
        with open(os.path.join(BASIC_DATA_PATH, "002總顧問學經歷格式化.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 總顧問學經歷", "content": f.read().replace("\n", "<br>")})
        # 第3張: 中藥局營業項目
        with open(os.path.join(BASIC_DATA_PATH, "003中藥局營業項目.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 中藥局營業項目", "content": f.read().replace("\n", "<br>")})
        # 第4張: 中藥局經營理念
        with open(os.path.join(BASIC_DATA_PATH, "004中藥局經營理念.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 中藥局經營理念", "content": f.read().replace("\n", "<br>")})
        # 第5張: 中藥局歷史源流
        with open(os.path.join(BASIC_DATA_PATH, "005中藥局歷史源流.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 中藥局歷史源流", "content": f.read().replace("\n", "<br>")})
        # 第6張: 中藥局診療日記
        with open(os.path.join(BASIC_DATA_PATH, "006中藥局診療日記1090101.txt"), "r", encoding="utf-8") as f:
            slides_data.append({"title": "竹文診所 - 中藥局診療日記", "content": f.read().replace("\n", "<br>")})

    except FileNotFoundError as e:
        error_message = f"缺少基本資料檔案，無法產生部分投影片：{e.filename}。請確保相關檔案已放置於 {BASIC_DATA_PATH} 目錄下。"
        # 即使部分檔案缺失，也繼續嘗試載入易經卦文

    yijing_titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
    if not os.path.exists(yijing_titles_path):
        if error_message:
            error_message += "\n同時也缺少易經標題檔案 (yijing標題.txt)，無法產生易經卦文投影片。"
        else:
            error_message = f"缺少易經標題檔案 ({yijing_titles_path})，無法產生易經卦文投影片。請確保該檔案存在。"
    else:
        try:
            with open(yijing_titles_path, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f if line.strip()]
            
            for i, title_name in enumerate(titles):
                gua_num = i + 1
                gua_file_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{gua_num}卦古原文無分斷點.txt")
                slide_content_html = f"易經古文共有64卦, 本段為第{gua_num}卦 {title_name}卦的條文<br>"
                
                if os.path.exists(gua_file_path):
                    with open(gua_file_path, "r", encoding="utf-8") as gf:
                        gua_text_lines = gf.readlines()
                    
                    if len(gua_text_lines) > 10:
                        slide_content_html += "".join(gua_text_lines[:10]).replace("\n", "<br>")
                        slide_content_html += "......<br>"
                        # 為了簡單起見，我們暫不實現點擊看全文的功能，但保留了原始腳本的意圖
                        # 實際應用中，可以提供一個連結指向完整的卦文頁面
                        # slide_content_html += f"<a href=\"#\" target=\"_new\">..我要看整段原文</a>" 
                    else:
                        slide_content_html += "".join(gua_text_lines).replace("\n", "<br>")
                    slides_data.append({"title": f"易經古文解析 - 第{gua_num}卦 {title_name}", "content": slide_content_html})
                else:
                    slides_data.append({"title": f"易經古文解析 - 第{gua_num}卦 {title_name}", "content": f"缺少第{gua_num}卦 ({title_name}) 的古文檔案 ({gua_file_path})"})
        except Exception as e:
            if error_message:
                error_message += f"\n讀取易經資料時發生錯誤: {str(e)}"
            else:
                error_message = f"讀取易經資料時發生錯誤: {str(e)}"

    return render_template("yijing_slides.html", slides=slides_data, error_message=error_message, title="易經古文解析講座")

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # 註冊藍圖
    app.register_blueprint(yijing_bp, url_prefix='/yijing')

    @app.route('/')
    def index():
        return render_template('index.html', title='易經互動網頁')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
