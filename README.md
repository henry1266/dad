# DAD 易經互動網頁

這個 repository 保存原始 Bash 工具、易經與網站素材，以及一個將主要流程逐步移植到 Python／Flask 的互動網頁。Python 應用可處理易經原文、產生卦文與投影片、整理維基百科內容，並顯示風水個案文字資料。

## 系統需求

- Python 3.10 以上
- UTF-8 檔案系統
- 只有執行維基百科下載功能時需要網路連線

## 安裝與啟動

在 repository 根目錄執行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r python/requirements.txt
export PYTHONPATH=python
export DAD_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python -m src.main
```

預設只監聽 `127.0.0.1:5003`。瀏覽器開啟本機的 5003 埠即可使用。

Windows PowerShell 啟用環境時，將 `source .venv/bin/activate` 改為：

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "python"
$env:DAD_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python -m src.main
```

## 重要環境變數

| 變數 | 預設值 | 用途 |
|---|---|---|
| `DAD_PROJECT_ROOT` | repository 根目錄 | 覆寫專案根路徑 |
| `DAD_BASH_SOURCE_DIR` | `<root>/bash` | Bash 原始素材來源 |
| `DAD_CONFIG_DATA_DIR` | `<root>/config_data` | 輸入、暫存與輸出資料根目錄 |
| `DAD_SECRET_KEY` | 每次啟動隨機產生 | Flask session 與 CSRF。正式使用務必固定設定 |
| `DAD_HOST` | `127.0.0.1` | 服務監聽位址 |
| `DAD_PORT` | `5003` | 服務埠號 |
| `DAD_DEBUG` | `0` | 設為 `1` 才啟用 Flask debugger |
| `DAD_AUTO_INITIALIZE` | `0` | 設為 `1` 才在啟動時自動建立核心資料 |
| `DAD_SESSION_COOKIE_SECURE` | `0` | HTTPS 部署時設為 `1` |
| `DAD_WIKIPEDIA_USER_AGENT` | 專案預設識別字串 | 覆寫維基百科請求識別 |

## 資料安全行為

- 啟動應用不會自動修改資料，除非明確設定 `DAD_AUTO_INITIALIZE=1`。
- 網頁中的資料處理選項預設皆未勾選。
- 「環境準備」預設只補上缺少的種子檔案，不覆寫使用者已修改的檔案。
- 程式產生的彙編內容使用具名區段更新，同一流程重跑不會重複附加。
- 表單包含 CSRF 驗證，服務預設只綁定本機。若要公開部署，仍應在反向代理或應用層加入身分驗證與 HTTPS。

## 測試

```bash
python -m pip install -r python/requirements-dev.txt
export PYTHONPATH=python
python -m compileall -q python/src
pytest -q
```

GitHub Actions 會在 Python 3.10 與 3.13 執行依賴檢查、語法編譯及測試。

## 主要目錄

- `bash/`：原始 Bash 程式與舊版素材
- `config_data/`：易經輸入、範本、暫存與生成資料
- `python/src/`：Flask 應用與 Python 處理模組
- `tests/`：回歸與安全行為測試

## 已知限制

- repository 仍保存大量歷史產物，包括已追蹤的虛擬環境、快取、備份檔與舊式 HTML 素材。本次僅新增忽略規則，未直接刪除歷史檔案，以免影響既有資料。
- Python 版本尚未完全取代 `d012.bash` 的所有文字轉換與樣板行為。應以實際輸出比對後再逐批遷移。
- 維基百科擷取依賴頁面結構，網站結構變更時可能需要調整清理規則。
