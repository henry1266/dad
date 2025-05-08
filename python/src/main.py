# 初始化 Flask 應用程式
import sys
import os
import glob
import re
import shutil # Added for file operations
from flask import Flask, render_template, Blueprint

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 設定固定資料夾路徑
# BASH_SOURCE_DIR is where the original bash script and its data files are located.
BASH_SOURCE_DIR = "/home/ubuntu/dad/bash"
# CONFIG_DATA_PATH is the working directory for the Python application, where data will be copied to and generated.
CONFIG_DATA_PATH = "/home/ubuntu/dad/config_data"

YIJING_INPUT_PATH = os.path.join(CONFIG_DATA_PATH, "易經輸入端資料夾")
YIJING_ANCIENT_TEXT_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存戰果資料夾")
BASIC_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "基本資料資料夾")
TOOL_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "工具程式資料夾") # For files like 掃垃圾文字.txt
HTML_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "HTML參考樣板資料夾")
SLIDES_TEMPLATE_PATH = os.path.join(CONFIG_DATA_PATH, "投影片參考樣板資料夾")
M_TXT_PATH = os.path.join(CONFIG_DATA_PATH, "m.txt")

# Directories for generated content, mirroring bash script structure but under CONFIG_DATA_PATH
YIJING_TOTAL_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經總戰果資料夾")
YIJING_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經戰果資料夾")
YIJING_INTERMEDIATE_PATH = os.path.join(CONFIG_DATA_PATH, "易經中間成品質料夾")
YIJING_MARKING_PATH = os.path.join(CONFIG_DATA_PATH, "易經標記資料夾")

YIJING_WIKI_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存戰果資料夾")
# YIJING_ANCIENT_TEXT_PATH is already defined for ancient text results
YIJING_HTML_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存戰果資料夾")
YIJING_SLIDES_RESULT_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存戰果資料夾")

# Parent directories for temporary files (numbered subfolders will be created by specific functions)
YIJING_WIKI_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經維基網資料暫存資料夾")
YIJING_ANCIENT_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存資料夾")
YIJING_HTML_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經HTML暫存資料夾")
YIJING_SLIDES_TEMP_PATH = os.path.join(CONFIG_DATA_PATH, "易經投影片暫存資料夾")

def prepare_environment():
    """Prepares the working environment by copying necessary files and creating directories."""
    print("Preparing environment...")
    os.makedirs(CONFIG_DATA_PATH, exist_ok=True)

    # Directories to copy from BASH_SOURCE_DIR
    dirs_to_copy = {
        "基本資料資料夾": BASIC_DATA_PATH,
        "易經輸入端資料夾": YIJING_INPUT_PATH,
        "工具程式資料夾": TOOL_DATA_PATH,
        "HTML參考樣板資料夾": HTML_TEMPLATE_PATH,
        "投影片參考樣板資料夾": SLIDES_TEMPLATE_PATH
    }

    for src_dirname, dest_path in dirs_to_copy.items():
        src_path = os.path.join(BASH_SOURCE_DIR, src_dirname)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"Warning: Source directory {src_path} not found.")
            os.makedirs(dest_path, exist_ok=True) # Create empty dir if source is missing, so other parts don't fail

    # Copy m.txt
    m_txt_src = os.path.join(BASH_SOURCE_DIR, "m.txt")    
    if os.path.exists(m_txt_src):
        shutil.copy2(m_txt_src, M_TXT_PATH)
        print(f"Copied {m_txt_src} to {M_TXT_PATH}")
    else:
        print(f"Warning: Source file {m_txt_src} not found.")

    # Directories to create under CONFIG_DATA_PATH
    dirs_to_create = [
        YIJING_TOTAL_RESULT_PATH, YIJING_RESULT_PATH, YIJING_INTERMEDIATE_PATH, YIJING_MARKING_PATH,
        YIJING_WIKI_RESULT_PATH, YIJING_ANCIENT_TEXT_PATH, YIJING_HTML_RESULT_PATH, YIJING_SLIDES_RESULT_PATH,
        YIJING_WIKI_TEMP_PATH, YIJING_ANCIENT_TEMP_PATH, YIJING_HTML_TEMP_PATH, YIJING_SLIDES_TEMP_PATH,
        # Specific subfolders from bash script like 易經總戰果1資料夾, 易經總戰果2資料夾 under 易經總戰果資料夾
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果1資料夾"),
        os.path.join(YIJING_TOTAL_RESULT_PATH, "易經總戰果2資料夾"),
    ]

    for path_to_create in dirs_to_create:
        os.makedirs(path_to_create, exist_ok=True)
        # print(f"Ensured directory exists: {path_to_create}") # Too verbose
    print("Environment preparation complete.")

def format_basic_data_files(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Basic data directory not found: {directory_path}")
        return
    source_files = glob.glob(os.path.join(directory_path, "*.txt"))
    for filepath in source_files:
        filename = os.path.basename(filepath)
        if filename.endswith("格式化.txt"):
            continue
        if filename.endswith(".txt") and os.path.isfile(filepath):
            output_filename = filename[:-4] + "格式化.txt"
            output_filepath = os.path.join(directory_path, output_filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f_in:
                    content = f_in.read()
                # Bash script: sed "s/\(..*\)\(  \)\(..*\)/\1 \&nbsp \3/" -> replace double space with space+nbsp+space
                # This python implementation replaces any two spaces with " &nbsp; "
                # The bash regex is a bit specific. Let's try to match it more closely if needed.
                # For now, using a simpler replace. The original was `content.replace("  ", " &nbsp; ")`
                # The sed command `sed "s/\(..*\)\(  \)\(..*\)/\1 \&nbsp \3/"` seems to target a specific pattern of two spaces surrounded by at least two characters on each side.
                # A direct translation of that sed is more complex. The existing python replace is simpler.
                # Let's stick to the existing simple replace for now, as it was in the original python code.
                formatted_content = content.replace("  ", " &nbsp; ")
                with open(output_filepath, "w", encoding="utf-8") as f_out:
                    f_out.write(formatted_content)
            except Exception as e:
                print(f"Error formatting file {filepath}: {e}")

def process_yijing_raw_text():
    source_yijing_file = os.path.join(YIJING_INPUT_PATH, "yijing.txt")
    output_processed_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing每卦到空列分隔全文文本有分斷點.txt")
    if not os.path.exists(source_yijing_file):
        print(f"Source Yijing file not found: {source_yijing_file}")
        return False
    # os.makedirs(YIJING_ANCIENT_TEXT_PATH, exist_ok=True) # Already created by prepare_environment
    try:
        with open(source_yijing_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        processed_lines = [line for line in lines if line.strip()] # grep -v '^$'
        temp_lines = []
        for line in processed_lines: # sed 's/%/&\n/p'; grep -v '%'
            if line.strip() != '%':
                temp_lines.append(line)
        processed_lines = temp_lines
        content = "".join(processed_lines)
        # sed 's/\(《易經》\)\(.*\)/\1\n\1\2/1'
        content = re.sub(r"(《易經》)(.*)", r"\1\n\1\2", content, 1)
        # sed 's/\(彖曰：\)\(.*\)/\\xxxx\n\1\2/1'
        content = re.sub(r"(彖曰：)(.*)", r"\\xxxx\n\1\2", content, 1)
        # sed 's/\(象曰：\)\(.*\)/\\xxx\n\1\2/1'
        content = re.sub(r"(象曰：)(.*)", r"\\xxx\n\1\2", content, 1)
        # sed 's/\(文言曰：\)\(.*\)/\\xx\n\1\2/1'
        content = re.sub(r"(文言曰：)(.*)", r"\\xx\n\1\2", content, 1)
        # sed 's/\(初.*：\)\(.*\)/\\xxxxx\n\1\2/1'
        content = re.sub(r"(初.*?：)(.*)", r"\\xxxxx\n\1\2", content, 1) # Made a slight correction to regex for '初.*：' to be non-greedy
        with open(output_processed_file, "w", encoding="utf-8") as f_out:
            f_out.write(content)
        print(f"Successfully processed yijing.txt to {output_processed_file}")
        return True
    except Exception as e:
        print(f"Error processing yijing.txt: {e}")
        return False

def generate_yijing_metadata_and_split_guas():
    processed_yijing_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing每卦到空列分隔全文文本有分斷點.txt")
    if not os.path.exists(processed_yijing_file):
        print(f"Processed Yijing file not found: {processed_yijing_file}. Run process_yijing_raw_text first.")
        return False

    try:
        with open(processed_yijing_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        header_pattern = re.compile(r"《易經》(第.*?卦)\s*([^\s]+)\s*([^\s]+)\s*([^\s]+)")
        
        titles = []
        orders = []
        order_title_details = [] # For yijing順序標題.txt
        wisdom_explanations = [] # For yijing標題列智慧解說.txt

        all_lines = content.splitlines()
        header_lines_info = []
        for i, line in enumerate(all_lines):
            match = header_pattern.match(line)
            if match:
                order_str = match.group(1).strip() # e.g., 第一卦
                title_str = match.group(2).strip() # e.g., 乾
                structure_str = match.group(3).strip() # e.g., 乾為天
                composition_str = match.group(4).strip() # e.g., 乾上乾下
                
                orders.append(order_str)
                titles.append(title_str)
                order_title_details.append(f"{order_str} {title_str}")
                wisdom_explanations.append(f"啟稟皇上,易經{order_str}是{title_str}卦!,本卦看起來是{structure_str}, 由{composition_str}組成!")
                header_lines_info.append({"order": order_str, "title": title_str, "line_index": i})

        if not titles:
            print("No Yijing titles found in processed file.")
            return False

        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt"), "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(titles) + "\n")
        print(f"Successfully generated yijing標題.txt")

        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing順序.txt"), "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(orders) + "\n")
        print(f"Successfully generated yijing順序.txt")
        
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing順序標題.txt"), "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(order_title_details) + "\n")
        print(f"Successfully generated yijing順序標題.txt")

        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題列智慧解說.txt"), "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(wisdom_explanations) + "\n")
        print(f"Successfully generated yijing標題列智慧解說.txt")

        for i in range(len(header_lines_info)):
            current_gua_info = header_lines_info[i]
            start_line_index = current_gua_info["line_index"]
            end_line_index = len(all_lines)
            if i + 1 < len(header_lines_info):
                next_gua_info = header_lines_info[i+1]
                end_line_index = next_gua_info["line_index"]
            
            gua_block_lines = all_lines[start_line_index:end_line_index]
            
            # Bash: sed -n '/[1-9]$/!p'; sed -n '/《易經》$/!p'; sed -n '/x$/!p'; grep -v '^$'
            # The python code was already doing grep -v '^$'
            # The markers \xxxx are at the start, sed -n '/x$/!p' removes lines *ending* with x.
            # The 《易經》 line to be removed is the one *starting* the next block, handled by slicing.
            # The [1-9]$ was for temporary numbers in bash, not present here.
            cleaned_gua_lines = [line for line in gua_block_lines if line.strip() and not line.endswith("x")] # Basic cleaning

            output_gua_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{i+1}卦古原文無分斷點.txt")
            with open(output_gua_file, "w", encoding="utf-8") as f_gua:
                f_gua.write("\n".join(cleaned_gua_lines) + "\n")
        print(f"Successfully generated 64 individual gua files.")
        return True

    except Exception as e:
        print(f"Error generating Yijing metadata or splitting guas: {e}")
        import traceback
        traceback.print_exc()
        return False

yijing_bp = Blueprint("yijing", __name__, template_folder="templates")

@yijing_bp.route("/slides")
def yijing_slides_lecture():
    slides_data = []
    error_message = None
    try:
        for i in range(1, 7):
            # Try formatted first, then unformatted
            formatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*格式化.txt")
            actual_files = glob.glob(formatted_file_pattern)
            actual_file_to_read = None
            base_name_part = ""

            if actual_files:
                actual_file_to_read = actual_files[0]
                base_name_part = os.path.basename(actual_file_to_read).replace("格式化.txt", "").split('.')[0][3:]
            else:
                unformatted_file_pattern = os.path.join(BASIC_DATA_PATH, f"{i:03d}*.txt")
                potential_files = glob.glob(unformatted_file_pattern)
                for pf in potential_files:
                    if not pf.endswith("格式化.txt"):
                        actual_file_to_read = pf
                        base_name_part = os.path.basename(actual_file_to_read).split('.')[0][3:]
                        break
            
            if not actual_file_to_read:
                 raise FileNotFoundError(f"No file matching {i:03d}*.txt or {i:03d}*格式化.txt found in {BASIC_DATA_PATH}.")

            slide_title_map = {
                "執行長學經歷": "竹文診所 - 執行長學經歷",
                "總顧問學經歷": "竹文診所 - 總顧問學經歷",
                "中藥局營業項目": "竹文診所 - 中藥局營業項目",
                "中藥局經營理念": "竹文診所 - 中藥局經營理念",
                "中藥局歷史源流": "竹文診所 - 中藥局歷史源流",
                "中藥局診療日記1090101": "竹文診所 - 中藥局診療日記"
            }
            current_slide_title = f"竹文診所 - {base_name_part}"
            for key_map, title_val in slide_title_map.items():
                # Use a more robust check, e.g. if base_name_part contains the key
                if key_map.replace(" ", "") in base_name_part.replace(" ", ""):
                    current_slide_title = title_val
                    break
            
            with open(actual_file_to_read, "r", encoding="utf-8") as f:
                slides_data.append({"title": current_slide_title, "content": f.read().replace("\n", "<br>")})

    except FileNotFoundError as e:
        error_message = f"缺少基本資料檔案，無法產生部分投影片：{str(e)}。請確保相關檔案已放置於 {BASIC_DATA_PATH} 目錄下。"
    except Exception as e:
        error_message = f"讀取基本資料投影片時發生錯誤: {str(e)}"

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
                    # Display first 10 lines, then ellipsis if more
                    display_lines = [line.replace("\n", "<br>") for line in gua_text_lines]
                    if len(display_lines) > 10:
                        slide_content_html += "".join(display_lines[:10])
                        slide_content_html += "......<br>"
                        # The link in bash was to a .txt file, here we might link to a full view if implemented
                        # slide_content_html += f"<a href=\"#\">..我要看整段原文</a><br>"
                    else:
                        slide_content_html += "".join(display_lines)
                    slides_data.append({"title": f"易經古文解析 - 第{gua_num}卦 {title_name}", "content": slide_content_html})
                else:
                    slides_data.append({"title": f"易經古文解析 - 第{gua_num}卦 {title_name}", "content": f"缺少第{gua_num}卦 ({title_name}) 的古文檔案 ({gua_file_path})"})
        except Exception as e:
            if error_message:
                error_message += f"\n讀取易經資料時發生錯誤: {str(e)}"
            else:
                error_message = f"讀取易經資料時發生錯誤: {str(e)}"
    return render_template("yijing_slides.html", slides=slides_data, error_message=error_message, title="易經古文解析講座")

def initialize_all_data():
    print("Running initial data processing...")
    prepare_environment() # New function to setup dirs and copy data
    format_basic_data_files(BASIC_DATA_PATH)
    if process_yijing_raw_text():
        generate_yijing_metadata_and_split_guas()
    # TODO: Add generation of dynamic sed-like processing (Python functions for text manipulation)
    print("Initial data processing complete.")

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(yijing_bp, url_prefix="/yijing")
    initialize_all_data() # Call data processing functions on app creation
    @app.route("/")
    def index():
        return render_template("index.html", title="易經互動網頁")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)

