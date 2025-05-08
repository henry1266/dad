# 初始化 Flask 應用程式
import sys
import os
from flask import Flask, render_template, Blueprint
import glob
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 設定固定資料夾路徑
CONFIG_DATA_PATH = "/home/ubuntu/dad/config_data"
YIJING_INPUT_PATH = os.path.join(CONFIG_DATA_PATH, "易經輸入端資料夾")
YIJING_ANCIENT_TEXT_PATH = os.path.join(CONFIG_DATA_PATH, "易經古原文暫存戰果資料夾")
BASIC_DATA_PATH = os.path.join(CONFIG_DATA_PATH, "基本資料資料夾")

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
    os.makedirs(YIJING_ANCIENT_TEXT_PATH, exist_ok=True)
    try:
        with open(source_yijing_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        processed_lines = [line for line in lines if line.strip()]
        temp_lines = []
        for line in processed_lines:
            if line.strip() != '%':
                temp_lines.append(line)
        processed_lines = temp_lines
        content = "".join(processed_lines)
        content = re.sub(r"(《易經》)(.*)", r"\1\n\1\2", content, 1)
        content = re.sub(r"(彖曰：)(.*)", r"\\xxxx\n\1\2", content, 1)
        content = re.sub(r"(象曰：)(.*)", r"\\xxx\n\1\2", content, 1)
        content = re.sub(r"(文言曰：)(.*)", r"\\xx\n\1\2", content, 1)
        content = re.sub(r"(初.*?：)(.*)", r"\\xxxxx\n\1\2", content, 1)
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
        
        # Extract headers: 《易經》第一卦  乾  乾為天  乾上乾下
        # Regex to capture the parts of the header lines
        header_pattern = re.compile(r"《易經》(第.*?卦)\s*([^\s]+)\s*([^\s]+)\s*([^\s]+)")
        
        titles = []
        orders = []
        # For splitting, we need to identify blocks for each gua
        # The bash script uses the order string (e.g., "第一卦") and "《易經》" as delimiters
        # Let's first get all header lines to extract titles and orders
        all_lines = content.splitlines()
        header_lines_info = []
        for i, line in enumerate(all_lines):
            match = header_pattern.match(line)
            if match:
                order_str = match.group(1).strip() # e.g., 第一卦
                title_str = match.group(2).strip() # e.g., 乾
                orders.append(order_str)
                titles.append(title_str)
                header_lines_info.append({"order": order_str, "title": title_str, "line_index": i})

        if not titles:
            print("No Yijing titles found in processed file.")
            return False

        # Save yijing標題.txt
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt"), "w", encoding="utf-8") as f_titles:
            for title in titles:
                f_titles.write(title + "\n")
        print(f"Successfully generated yijing標題.txt")

        # Save yijing順序.txt
        with open(os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing順序.txt"), "w", encoding="utf-8") as f_orders:
            for order in orders:
                f_orders.write(order + "\n")
        print(f"Successfully generated yijing順序.txt")

        # Split into individual gua files
        for i in range(len(header_lines_info)):
            current_gua_info = header_lines_info[i]
            start_line_index = current_gua_info["line_index"]
            end_line_index = len(all_lines)
            if i + 1 < len(header_lines_info):
                next_gua_info = header_lines_info[i+1]
                # Find the line 《易經》 that starts the next gua's header, or the header itself
                # The bash script uses `sed -n "/$course/,/《易經》$/p"`, then removes the last `《易經》` line.
                # This implies it takes lines until the *next* `《易經》` marker.
                # So, we search for the line index of the next header.
                end_line_index = next_gua_info["line_index"]
            
            gua_block_lines = all_lines[start_line_index:end_line_index]
            
            # Clean up the block: remove header, x markers, empty lines
            # The first line is the header, which we don't want in the split file's content usually, or it's processed differently.
            # The bash script: sed -n '/[1-9]$/!p' (removes lines ending with a digit - the temp number)
            # sed -n '/《易經》$/!p' (removes the 《易經》 leader line)
            # sed -n '/x$/!p' (removes lines ending with x - the markers)
            # grep -v '^$' (remove empty lines)
            
            # For yijing切開第N卦古原文無分斷點.txt, the bash script seems to keep the content after the header.
            # Let's refine the content extraction for the split file.
            # The bash script's logic for splitting: 
            # sed -n "/$course/,/《易經》$/p" -> gets the block including the current header and up to (but not including) the next header's start.
            # Then it does: sed -n '/[1-9]$/!p'; sed -n '/《易經》$/!p'; sed -n '/x$/!p'; grep -v '^$'
            # This means the first line (header) is included in the block, then specific lines are removed.

            # Let's simplify: take lines from the header line, up to the next header line (exclusive).
            # Then, from this block, remove the markers and empty lines.
            # The bash script does not seem to remove the first header line from the *content* of yijing切開第N卦古原文無分斷點.txt
            # It just uses it for naming/identification.
            
            # The file yijing切開第$i卦古原文無分斷點.txt should contain the text of the gua.
            # The bash script's `sed -n "/$course/,/《易經》$/p"` captures the block.
            # Then `sed -n '/《易經》$/!p'` removes the *next* `《易經》` line if it was captured.
            # `sed -n '/[1-9]$/!p'` was for a temporary number, not relevant here if we iterate by index.
            # `sed -n '/x$/!p'` removes lines ending with x (our \xxxx, \xxx markers).
            # `grep -v '^$'` removes empty lines.

            cleaned_gua_lines = []
            for line_idx, line_content in enumerate(gua_block_lines):
                # The bash script removes the 《易經》 line that acts as a separator for the *next* gua.
                # Our slicing `all_lines[start_line_index:end_line_index]` already handles this.
                temp_line = line_content
                if temp_line.startswith("\\xxxx") or temp_line.startswith("\\xxx") or temp_line.startswith("\\xx") or temp_line.startswith("\\xxxxx"):
                    # These markers were for the *first* instance in the whole file, not per gua in this context of splitting.
                    # The bash script applies these markers to the *whole file first*, then splits.
                    # So, the split content will contain these markers if they fall within the gua's section.
                    # The later sed '/x$/!p' would remove lines *ending* with 'x'. Our markers are at the start.
                    # Let's assume the markers should be kept if they are part of the gua's text as per d012.bash logic.
                    # The d012.bash `sed -n '/x$/!p'` seems to target lines *ending* with x, not starting with `\xxxx`.
                    # Let's re-evaluate: the `yijing每卦到空列分隔全文文本有分斷點.txt` *contains* these markers.
                    # The splitting logic `sed -n "/$course/,/《易經》$/p"` gets the block.
                    # Then `sed -n '/x$/!p'` is applied. This means if a line *ends* with 'x', it's removed.
                    # Our markers `\xxxx` etc. do not end with 'x'. So they would be kept by this rule.
                    pass # Keep the line with markers for now, as per apparent bash logic.
                
                if line_content.strip(): # Effectively grep -v '^$'
                    cleaned_gua_lines.append(line_content)
            
            # The bash script's output for yijing切開第N卦古原文無分斷點.txt seems to be just the text lines of the gua.
            # It doesn't explicitly show removal of the main header of *that* gua from its own file.
            # Let's assume the first line (header) is part of the content for now.

            output_gua_file = os.path.join(YIJING_ANCIENT_TEXT_PATH, f"yijing切開第{i+1}卦古原文無分斷點.txt")
            with open(output_gua_file, "w", encoding="utf-8") as f_gua:
                f_gua.write("\n".join(cleaned_gua_lines))
            # print(f"Successfully generated {output_gua_file}") # Too verbose for 64 files
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
            file_path = os.path.join(BASIC_DATA_PATH, f"{i:03d}*格式化.txt")
            actual_files = glob.glob(file_path)
            if not actual_files:
                # Try without formatting if formatted not found (e.g. 003, 004, 005, 006 might not have been formatted by original bash)
                file_path_orig = os.path.join(BASIC_DATA_PATH, f"{i:03d}*.txt") 
                actual_files_orig = glob.glob(file_path_orig)
                # Find non-formatted version if it exists and is not the formatted one
                non_formatted_file = None
                for f_orig in actual_files_orig:
                    if not f_orig.endswith("格式化.txt"):
                        non_formatted_file = f_orig
                        break
                if not non_formatted_file:
                    raise FileNotFoundError(f"No file matching {file_path} or {file_path_orig} (non-formatted) found.")
                actual_file_to_read = non_formatted_file
                # Determine title based on filename (simplified)
                base_name = os.path.basename(actual_file_to_read).split('.')[0][3:] # Remove 00N and extension
            else:
                actual_file_to_read = actual_files[0]
                base_name = os.path.basename(actual_file_to_read).replace("格式化.txt", "").split('.')[0][3:]
            
            # Create a more generic title
            slide_title_map = {
                "執行長學經歷": "竹文診所 - 執行長學經歷",
                "總顧問學經歷": "竹文診所 - 總顧問學經歷",
                "中藥局營業項目": "竹文診所 - 中藥局營業項目",
                "中藥局經營理念": "竹文診所 - 中藥局經營理念",
                "中藥局歷史源流": "竹文診所 - 中藥局歷史源流",
                "中藥局診療日記1090101": "竹文診所 - 中藥局診療日記"
            }
            # Find a key in slide_title_map that base_name starts with
            current_slide_title = f"竹文診所 - {base_name}" # Default title
            for key_map, title_val in slide_title_map.items():
                if base_name.startswith(key_map.replace(" ", "")):
                    current_slide_title = title_val
                    break
            
            with open(actual_file_to_read, "r", encoding="utf-8") as f:
                slides_data.append({"title": current_slide_title, "content": f.read().replace("\n", "<br>")})

    except FileNotFoundError as e:
        error_message = f"缺少基本資料檔案，無法產生部分投影片：{str(e)}。請確保相關檔案已放置於 {BASIC_DATA_PATH} 目錄下。"

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

def initialize_all_data():
    print("Running initial data processing...")
    format_basic_data_files(BASIC_DATA_PATH)
    if process_yijing_raw_text():
        generate_yijing_metadata_and_split_guas()
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

