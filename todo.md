## Python 互動網頁功能補齊任務列表

### 一、環境設定與初始化

- [X] 完整複製範本資料夾功能 (工具程式、基本資料、HTML參考樣板、投影片參考樣板、易經輸入端)。 (部分實現於 `prepare_environment`)
- [X] 驗證並擴充基本資料文字檔格式化功能 (空格轉 `&nbsp;`)，確保與 `d012.bash` 一致。 (已在 `main.py` 中實現 `format_basic_data_files`)
- [X] 實現清理並建立各種處理過程中的暫存與結果資料夾的功能。 (已在 `main.py` 的 `prepare_environment` 中實現)
- [ ] 以 Python 實現動態文本處理腳本生成 (取代 `sed` 腳本：垃圾字詞清理、專有名詞維基連結、易經標題維基連結等)。

### 二、維基百科資料下載與處理 (自選主題)

- [X] 實現讀取自選專有名詞列表功能。 (已在 `main.py` 中實現 `process_custom_topics_wiki`)
- [X] 使用 Python (如 `requests` 和 `BeautifulSoup4`) 下載對應維基頁面 (取代 `w3m`)。 (已在 `main.py` 中實現 `get_wiki_content_basic` 和 `process_custom_topics_wiki`)
- [X] 實現清理下載內容 (去空白行、去垃圾字詞、擷取相關段落) 的 Python 邏輯。 (已在 `main.py` 中實現 `get_wiki_content_basic`)
- [X] 實現彙整結果至 `自選專有名詞維基文獻.txt` 及 `我的著作文獻部份.txt` 的功能。 (已在 `main.py` 中實現 `process_custom_topics_wiki`)

### 三、易經古文處理

- [X] 驗證並擴充 `yijing.txt` 處理功能 (斷句、分段)，確保與 `d012.bash` 一致。 (已在 `main.py` 中實現 `process_yijing_raw_text`)
- [ ] 實現產生所有必要的易經元數據檔案：
    - [X] `yijing標題.txt` (現有功能驗證與補齊) (已在 `main.py` 中實現 `generate_yijing_metadata_and_split_guas`)
    - [X] `yijing順序.txt` (現有功能驗證與補齊) (已在 `main.py` 中實現 `generate_yijing_metadata_and_split_guas`)
    - [X] `yijing順序標題.txt` (已在 `main.py` 中實現 `generate_yijing_metadata_and_split_guas`)
    - [X] `yijing標題列智慧解說.txt` (已在 `main.py` 中實現 `generate_yijing_metadata_and_split_guas`)
- [X] 驗證並擴充將易經全文分割為64個獨立卦文檔案的功能，確保與 `d012.bash` 一致。 (已在 `main.py` 中實現 `generate_yijing_metadata_and_split_guas`)

### 四、非互動式投影片生成 (HTML, impress.js 格式)

- [X] **類型一：易經各卦全文投影片 (`投影片秀易經古文解析講座$course.html`)** (已在 `main.py` 中實現 `yijing_slides_lecture_ancient`)
    - [X] 實現包含基本資料的投影片內容生成。
    - [X] 實現逐卦顯示全文或摘要，並提供完整原文連結的功能。
    - [X] 使用 Python 和 Flask 模板引擎 (取代 HTML 樣板與 `sed`) 生成 impress.js 格式投影片。
- [X] **類型二：易經卦駁段與媽傳記投影片 (`投影片秀易經古文解析講座卦駁段$course.html`)** (已在 `main.py` 中實現 `yijing_slides_lecture_guaci_moms_records`)
    - [X] 實現包含出版社資料、基本資料的投影片內容生成。
    - [X] 實現組合媽手記相片、記事本、媽文章、生活照、演講、變色盤、易經卦駁段等內容的功能。
    - [X] 實現整合 `m.txt` (媽的寫作內容) 的功能。
    - [X] 使用 Python 和 Flask 模板引擎生成 impress.js 格式投影片。
- [X] **類型三：易經彖象段投影片 (`投影片秀易經古文解析講座彖象段$course.html`)** (已在 `main.py` 中實現 `yijing_slides_lecture_tuanxiang`)
    - [X] 實現包含基本資料的投影片內容生成。
    - [X] 實現擷取並展示每卦的彖辭與象辭的功能。
    - [X] 使用 Python 和 Flask 模板引擎生成 impress.js 格式投影片。

### 五、維基百科資料下載與處理 (易經64卦)

- [X] 實現讀取64卦卦名 (來自 `yijing標題.txt`) 功能。 (已在 `main.py` 中實現 `process_yijing_guas_wiki`)
- [X] 使用 Python (如 `requests` 和 `BeautifulSoup4`) 下載對應維基頁面。 (已在 `main.py` 中實現 `get_wiki_content_basic`)
- [X] 實現清理下載內容 (同自選主題處理方式) 的 Python 邏輯。 (已在 `main.py` 中實現 `get_wiki_content_basic`)
- [X] 實現彙整結果至 `yijing卦名維基文獻.txt` 及 `我的著作文獻部份.txt` 的功能。 (已在 `main.py` 中實現 `process_yijing_guas_wiki`)

### 六、HTML網頁生成 (每卦一個網頁)

- [X] 實現針對特定範圍卦的網頁生成功能 (預設或可配置)。 (已在 `main.py` 中實現 `gua_page` 路由，目前生成所有64卦)
- [X] 實現組合該卦古文、維基百科資料的功能。 (已在 `main.py` 中實現 `gua_page` 路由和 `gua_page.html` 模板)
- [ ] 實現內容中專有名詞、易經標題等自動加上維基連結的功能。
- [X] 實現包含多個外部連結 (谷歌、百度、國家中醫藥研究所、PubMed 等) 的功能。 (已在 `main.py` 中實現 `gua_page` 路由和 `gua_page.html` 模板)
- [X] 使用 Python 和 Flask 模板引擎 (取代 HTML 樣板與 `sed`) 生成獨立網頁。 (已在 `main.py` 中實現 `gua_page` 路由和 `gua_page.html` 模板)

### 七、書稿彙整 (`我的著作文獻部份.txt`)

- [X] 實現將處理過的自選主題維基文獻、64卦維基文獻、易經古文等內容逐步附加到此檔案的功能。 (已在 `main.py` 的 `process_custom_topics_wiki`, `process_yijing_guas_wiki`, 和 `append_ancient_texts_to_compilation` 中實現)

### 八、風水個案分析網頁生成

- [X] 實現讀取 `易經個案列表.txt` 的功能。 (已在 `main.py` 的 `index` 路由中實現)
- [X] 實現讀取個案相關資料檔案的功能。 (已在 `main.py` 的 `fengshui_case_page` 路由中實現)
- [X] 使用 Python 和 Flask 模板引擎 (取代 HTML 樣板與 `sed`) 生成個案分析網頁。 (已在 `main.py` 中實現 `fengshui_case_page` 路由和 `fengshui_case_page.html` 模板)

### 九、使用者互動

- [X] 實現讓使用者透過網頁介面指定處理範圍 (例如：卦的起訖、樣板選擇等) 的功能。 (已在 `main.py` 和 `index.html` 中實現互動表單與處理邏輯)

### 十、其他與整合

- [ ] 實現完整的資料夾結構複製與管理 (若 `d012.bash` 中有更複雜的邏輯)。
- [ ] 確保所有 Python 實現的功能與 Flask 應用程式正確整合。
- [ ] 實現清理執行過程中產生的暫存資料夾的功能。
- [ ] 安裝必要的 Python 套件 (如 `requests`, `beautifulsoup4`)。

