# DAD Reading Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved reading-first DAD experience with one content catalog, unified title search, honest missing-data states, a separate processing workspace, consistent editorial layouts, and improved impress.js controls.

**Architecture:** Keep Flask and Jinja as the complete rendering path, introduce a filesystem-backed `ContentCatalog` as the single source for readable-content metadata, and use small vanilla-JavaScript modules only for progressive enhancement. Move processing orchestration into a focused module that returns structured step results, while leaving generated content and the existing impress.js slide data untouched.

**Tech Stack:** Python 3.10+, Flask 3.1, Jinja, MarkupSafe, vanilla JavaScript, CSS, impress.js, pytest 9.

**Spec:** `docs/superpowers/specs/2026-08-23-reading-experience-design.md`

## Global Constraints

- Preserve all pre-existing `config_data` modifications and untracked generated directories; never stage them in feature commits.
- Do not move, rewrite, or synthesize user content files. Read fengshui case lists and case files from `YIJING_INPUT_PATH`.
- Remove `FENGSHUI_CASES_PATH`, the home-page processing form, `POST /process_interaction`, and the `generate_all_outputs` control without compatibility forwarding.
- Add no production dependency, frontend framework, JSON search API, cross-request catalog cache, database, or background queue.
- Keep server-rendered content complete when JavaScript is unavailable.
- Keep the three current slide routes, their generated slide content, media assets, coordinates, and impress.js engine.
- Retain CSRF protection, range limits `1..10_000`, maximum inclusive span `50`, safe defaults, HTML autoescaping, and `DAD_AUTO_INITIALIZE=0` behavior.
- Use the approved palette: warm paper background, ink green primary, restrained brass accent; statuses must include text and never rely on color alone.
- Support keyboard focus, semantic landmarks, `prefers-reduced-motion`, a two-column-to-one-column mobile collapse, and no horizontal viewport overflow.
- On this checkout, prefix every Git subcommand with `git -c safe.directory='%(prefix)///192.168.68.68/node/dad'` and stage only files named in each task.
- Before each commit, run `git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only` and verify it lists only that task's files.

## File Responsibility Map

- `python/src/content_catalog.py`: immutable content metadata, filesystem discovery, availability, normalized search text, counts, lookup, and adjacency.
- `python/src/processing.py`: immutable processing selections/results and ordered orchestration of existing processing functions.
- `python/src/main.py`: Flask app assembly, home/workspace routes, HTTP form parsing, flash serialization, CSRF, error handlers, and optional startup initialization.
- `python/src/page_generator.py`: gua and fengshui detail routes; reading data assembly and HTTP status semantics.
- `python/src/config.py`: canonical data paths; no separate fengshui case path.
- `python/src/data_processor.py`: existing file transformations and environment preparation; no separate case-directory copy.
- `python/src/templates/base.html`: shared non-slide landmarks, navigation, page blocks, CSS and script extension points.
- `python/src/templates/index.html`: catalog search, filters, statistics, cards, unavailable states, and workspace callout.
- `python/src/templates/workspace.html`: grouped processing form and structured result list.
- `python/src/templates/gua_page.html`: gua reading sections and previous/next navigation.
- `python/src/templates/fengshui_case_page.html`: available-case reading page.
- `python/src/templates/error.html`: shared friendly HTTP error page.
- `python/src/templates/impress_slides_base.html`: slide toolbar markup and impress initialization.
- `python/src/static/style.css`: all non-slide design tokens, components, responsive layout, focus, and reduced motion.
- `python/src/static/catalog.js`: title search and type filtering only.
- `python/src/static/workspace.js`: operation-dependent fields and guarded submit-state enhancement.
- `python/src/static/slides-controls.css`: slide toolbar and media presentation.
- `python/src/static/slides-controls.js`: previous/next, counter, help panel, and impress event handling.
- `tests/test_content_catalog.py`: catalog discovery, availability, normalization, counts, lookup, and adjacency.
- `tests/test_processing.py`: structured processing reports, ordering, failure isolation, and empty selection.
- `tests/conftest.py`: reload-safe Flask application fixture for route tests.
- `tests/test_flask_app.py`: home, workspace, CSRF, PRG, gua, case, and 404 behavior.
- `tests/test_repository_layout.py`: template/static wiring, progressive-enhancement and accessibility guardrails.
- `README.md`: updated routes, reading/search behavior, workspace safety, and slide controls.
- `.gitignore`: ignore `.superpowers/` visual-companion artifacts.

---

### Task 1: Canonical Content Catalog

**Files:**
- Create: `python/src/content_catalog.py`
- Create: `tests/test_content_catalog.py`
- Modify: `python/src/config.py:26-35`
- Modify: `python/src/data_processor.py:8-80`
- Modify: `tests/test_data_processor.py:11-39`

**Interfaces:**
- Consumes: `YIJING_ANCIENT_TEXT_PATH` and `YIJING_INPUT_PATH` from `src.config`.
- Produces: `ContentEntry`, `ContentCatalog`, `normalize_search_text(*parts: object) -> str`, and `build_content_catalog(*, ancient_text_path: str | os.PathLike[str] | None = None, yijing_input_path: str | os.PathLike[str] | None = None) -> ContentCatalog`.
- Produces methods used by later tasks: `ContentCatalog.entries_for(kind)`, `find(kind, key)`, `adjacent(kind, key)`, `total_count(kind)`, and `available_count(kind)`.

- [ ] **Step 1: Write catalog discovery and availability tests**

Create `tests/test_content_catalog.py` with complete fixture construction and explicit assertions:

```python
from pathlib import Path

from src.content_catalog import build_content_catalog, normalize_search_text


def _catalog_fixture(tmp_path: Path) -> tuple[Path, Path]:
    ancient = tmp_path / "ancient"
    inputs = tmp_path / "inputs"
    ancient.mkdir()
    inputs.mkdir()
    titles = ["乾", "坤", "屯"]
    (ancient / "yijing標題.txt").write_text("\n".join(titles) + "\n", encoding="utf-8")
    for number in range(1, 4):
        (ancient / f"yijing切開第{number}卦古原文無分斷點.txt").write_text(
            f"第 {number} 卦內容\n", encoding="utf-8"
        )
    (inputs / "易經個案列表.txt").write_text("易經個案001\n易經個案002\n", encoding="utf-8")
    (inputs / "易經個案001.txt").write_text("可閱讀個案\n", encoding="utf-8")
    return ancient, inputs


def test_catalog_discovers_guas_slides_and_case_availability(tmp_path):
    ancient, inputs = _catalog_fixture(tmp_path)
    catalog = build_content_catalog(
        ancient_text_path=ancient,
        yijing_input_path=inputs,
    )

    assert [entry.title for entry in catalog.entries_for("gua")] == ["乾", "坤", "屯"]
    assert catalog.total_count("slides") == 3
    assert catalog.total_count("fengshui_case") == 2
    assert catalog.available_count("fengshui_case") == 1
    assert catalog.find("fengshui_case", "易經個案001").url == "/fengshui/case/%E6%98%93%E7%B6%93%E5%80%8B%E6%A1%88001"
    missing = catalog.find("fengshui_case", "易經個案002")
    assert missing.available is False
    assert missing.url is None
    assert missing.unavailable_reason == "缺少內容檔"


def test_catalog_normalizes_search_and_guards_adjacency(tmp_path):
    ancient, inputs = _catalog_fixture(tmp_path)
    catalog = build_content_catalog(ancient_text_path=ancient, yijing_input_path=inputs)

    assert normalize_search_text(" 第 1 卦 ", "乾", "GUA") == "第 1 卦 乾 gua"
    assert "第 1 卦" in catalog.find("gua", "1").search_text
    assert catalog.adjacent("gua", "1")[0] is None
    assert catalog.adjacent("gua", "1")[1].key == "2"
    assert catalog.adjacent("gua", "3")[1] is None


def test_catalog_represents_64_guas_three_slides_and_ten_cases(tmp_path):
    ancient = tmp_path / "ancient"
    inputs = tmp_path / "inputs"
    ancient.mkdir()
    inputs.mkdir()
    (ancient / "yijing標題.txt").write_text(
        "\n".join(f"卦名{number:02d}" for number in range(1, 65)) + "\n",
        encoding="utf-8",
    )
    (inputs / "易經個案列表.txt").write_text(
        "\n".join(f"易經個案{number:03d}" for number in range(1, 11)) + "\n",
        encoding="utf-8",
    )
    (inputs / "易經個案001.txt").write_text("可閱讀個案\n", encoding="utf-8")

    catalog = build_content_catalog(
        ancient_text_path=ancient,
        yijing_input_path=inputs,
    )

    assert catalog.total_count("gua") == 64
    assert catalog.total_count("slides") == 3
    assert catalog.total_count("fengshui_case") == 10
    assert catalog.available_count("fengshui_case") == 1
    assert all(
        entry.unavailable_reason == "缺少內容檔"
        for entry in catalog.entries_for("fengshui_case")[1:]
    )
```

- [ ] **Step 2: Run the new tests and verify the module is missing**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_content_catalog.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'src.content_catalog'`.

- [ ] **Step 3: Create the immutable catalog types and query methods**

Create `python/src/content_catalog.py` with these public types and methods:

```python
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH

ContentKind = Literal["gua", "slides", "fengshui_case"]


@dataclass(frozen=True, slots=True)
class ContentEntry:
    kind: ContentKind
    key: str
    title: str
    url: str | None
    available: bool
    unavailable_reason: str | None
    search_text: str
    number: int | None = None


@dataclass(frozen=True, slots=True)
class ContentCatalog:
    entries: tuple[ContentEntry, ...]
    warnings: tuple[str, ...] = ()

    def entries_for(self, kind: ContentKind) -> tuple[ContentEntry, ...]:
        return tuple(entry for entry in self.entries if entry.kind == kind)

    def find(self, kind: ContentKind, key: str) -> ContentEntry | None:
        return next(
            (entry for entry in self.entries if entry.kind == kind and entry.key == str(key)),
            None,
        )

    def adjacent(
        self, kind: ContentKind, key: str
    ) -> tuple[ContentEntry | None, ContentEntry | None]:
        entries = self.entries_for(kind)
        index = next((i for i, entry in enumerate(entries) if entry.key == str(key)), None)
        if index is None:
            return None, None
        previous = entries[index - 1] if index > 0 else None
        following = entries[index + 1] if index + 1 < len(entries) else None
        return previous, following

    def total_count(self, kind: ContentKind) -> int:
        return len(self.entries_for(kind))

    def available_count(self, kind: ContentKind) -> int:
        return sum(entry.available for entry in self.entries_for(kind))


def normalize_search_text(*parts: object) -> str:
    return " ".join(" ".join(str(part).split()) for part in parts if part is not None).casefold()
```

- [ ] **Step 4: Implement filesystem discovery for all three content kinds**

In the same file, define the fixed slide entries and the builder. Preserve list order, strip `.txt` from case keys, and attach a warning rather than raising when a list file is missing:

```python
_SLIDES = (
    ("lecture_ancient", "易經古文解析講座（全文）", "/slides/lecture_ancient"),
    ("lecture_guaci_moms_records", "易經卦辭與媽傳記講座", "/slides/lecture_guaci_moms_records"),
    ("lecture_tuanxiang", "易經彖象解析講座", "/slides/lecture_tuanxiang"),
)


def _read_nonempty_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_content_catalog(
    *,
    ancient_text_path: str | os.PathLike[str] | None = None,
    yijing_input_path: str | os.PathLike[str] | None = None,
) -> ContentCatalog:
    ancient = Path(ancient_text_path or YIJING_ANCIENT_TEXT_PATH)
    inputs = Path(yijing_input_path or YIJING_INPUT_PATH)
    entries: list[ContentEntry] = []
    warnings: list[str] = []

    titles_path = ancient / "yijing標題.txt"
    titles = _read_nonempty_lines(titles_path)
    if not titles:
        warnings.append("尚未找到卦名資料，請前往資料工作台產生易經元數據。")
    for number, title in enumerate(titles, start=1):
        entries.append(
            ContentEntry(
                kind="gua",
                key=str(number),
                number=number,
                title=title,
                url=f"/gua/{number}",
                available=True,
                unavailable_reason=None,
                search_text=normalize_search_text(f"第 {number} 卦", number, title, "六十四卦", "gua"),
            )
        )

    for key, title, url in _SLIDES:
        entries.append(
            ContentEntry(
                kind="slides",
                key=key,
                title=title,
                url=url,
                available=True,
                unavailable_reason=None,
                search_text=normalize_search_text(title, "投影片", "講座", "slides"),
            )
        )

    case_list_path = inputs / "易經個案列表.txt"
    case_names = _read_nonempty_lines(case_list_path)
    if not case_list_path.is_file():
        warnings.append("尚未找到風水個案清單。")
    for raw_name in case_names:
        key = raw_name.removesuffix(".txt")
        case_path = inputs / f"{key}.txt"
        available = case_path.is_file()
        entries.append(
            ContentEntry(
                kind="fengshui_case",
                key=key,
                title=key,
                url=f"/fengshui/case/{quote(key, safe='')}" if available else None,
                available=available,
                unavailable_reason=None if available else "缺少內容檔",
                search_text=normalize_search_text(key, "風水個案", "fengshui case"),
            )
        )
    return ContentCatalog(tuple(entries), tuple(warnings))
```

- [ ] **Step 5: Remove the unused second fengshui directory contract**

Delete `FENGSHUI_CASES_PATH` from `python/src/config.py`, remove it from the imports and `dirs_to_copy` mapping in `python/src/data_processor.py`, and delete the corresponding monkeypatch entry in `tests/test_data_processor.py`. Do not touch any directory under `config_data`.

- [ ] **Step 6: Run focused catalog and environment tests**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_content_catalog.py tests/test_config.py tests/test_data_processor.py -q
```

Expected: all focused tests pass.

- [ ] **Step 7: Commit the catalog boundary**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/content_catalog.py python/src/config.py python/src/data_processor.py tests/test_content_catalog.py tests/test_data_processor.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "feat: add canonical content catalog"
```

Expected staged files: exactly the five paths in the `git add` command.

---

### Task 2: Detail Route Status and Test Fixture

**Files:**
- Create: `tests/conftest.py`
- Modify: `tests/test_flask_app.py:1-109`
- Modify: `python/src/page_generator.py:1-116`

**Interfaces:**
- Consumes: `build_content_catalog()`, `ContentCatalog.find()`, `ContentCatalog.adjacent()`, `YIJING_INPUT_PATH`, and `resolve_existing_child()`.
- Produces: gua context keys `gua_data`, `previous_entry`, `next_entry`; case context key `case_data`; HTTP 404 for unknown/out-of-range/missing content.
- Produces pytest fixture `app_factory() -> tuple[Flask, Path]`, where the `Path` is the temporary `DAD_CONFIG_DATA_DIR`.

- [ ] **Step 1: Extract a reload-safe Flask fixture**

Create `tests/conftest.py` and move the current `_load_app` logic into this fixture. Do not create `易經個案資料夾`; cases belong in the input directory:

```python
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.fixture
def app_factory(monkeypatch, tmp_path):
    def create():
        data = tmp_path / "data"
        (data / "易經古原文暫存戰果資料夾").mkdir(parents=True, exist_ok=True)
        (data / "易經輸入端資料夾").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("DAD_PROJECT_ROOT", str(tmp_path))
        monkeypatch.setenv("DAD_CONFIG_DATA_DIR", str(data))
        monkeypatch.setenv("DAD_SECRET_KEY", "test-secret")
        monkeypatch.setenv("DAD_AUTO_INITIALIZE", "0")

        import src.config as config
        importlib.reload(config)
        import src.content_catalog as content_catalog
        import src.data_processor as data_processor
        import src.wiki_handler as wiki_handler
        import src.slide_generator as slide_generator
        import src.page_generator as page_generator
        import src.main as main

        for module in (
            content_catalog,
            data_processor,
            wiki_handler,
            slide_generator,
            page_generator,
            main,
        ):
            importlib.reload(module)
        return main.create_app({"TESTING": True}), data

    return create
```

Update existing route tests to use `app, data = app_factory()` and delete `_load_app`.

- [ ] **Step 2: Write failing HTTP-semantics tests**

Add these tests to `tests/test_flask_app.py`:

```python
def _seed_two_guas(data):
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text("乾\n坤\n", encoding="utf-8")
    (ancient / "yijing切開第1卦古原文無分斷點.txt").write_text("乾：元亨利貞。\n", encoding="utf-8")
    (ancient / "yijing切開第2卦古原文無分斷點.txt").write_text("坤：元亨。\n", encoding="utf-8")


def test_gua_route_returns_404_outside_catalog(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    client = app.test_client()

    assert client.get("/gua/1").status_code == 200
    assert client.get("/gua/3").status_code == 404
    assert client.get("/gua/65").status_code == 404


def test_all_64_catalog_gua_routes_are_readable(app_factory):
    app, data = app_factory()
    ancient = data / "易經古原文暫存戰果資料夾"
    (ancient / "yijing標題.txt").write_text(
        "\n".join(f"卦名{number:02d}" for number in range(1, 65)) + "\n",
        encoding="utf-8",
    )
    client = app.test_client()

    assert [client.get(f"/gua/{number}").status_code for number in range(1, 65)] == [
        200
    ] * 64


def test_fengshui_route_reads_input_directory_and_missing_is_404(app_factory):
    app, data = app_factory()
    inputs = data / "易經輸入端資料夾"
    (inputs / "易經個案列表.txt").write_text("易經個案001\n易經個案002\n", encoding="utf-8")
    (inputs / "易經個案001.txt").write_text("可閱讀內容\n", encoding="utf-8")
    client = app.test_client()

    available = client.get("/fengshui/case/易經個案001")
    missing = client.get("/fengshui/case/易經個案002")
    unknown = client.get("/fengshui/case/不存在")

    assert available.status_code == 200
    assert "可閱讀內容" in available.get_data(as_text=True)
    assert missing.status_code == 404
    assert unknown.status_code == 404
```

Also update the existing escaping test so it writes `測試.txt` into `易經輸入端資料夾` and includes `測試` in `易經個案列表.txt`.

- [ ] **Step 3: Run route tests and verify old status behavior fails**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py -q
```

Expected: out-of-catalog gua and missing fengshui case assertions fail because the current routes render HTTP 200 error pages.

- [ ] **Step 4: Make gua lookup and adjacency catalog-driven**

Replace exception-to-error-page handling for invalid gua identifiers with catalog lookup and `abort(404)`, while preserving per-section missing-content messages:

```python
from flask import Blueprint, abort, render_template

from .content_catalog import build_content_catalog


def _load_gua_data(gua_number: int, title: str) -> dict[str, object]:
    ancient_text_file = os.path.join(
        YIJING_ANCIENT_TEXT_PATH,
        f"yijing切開第{gua_number}卦古原文無分斷點.txt",
    )
    if os.path.isfile(ancient_text_file):
        with open(ancient_text_file, "r", encoding="utf-8") as handle:
            ancient_text = "\n".join(
                re.sub(r"\\[xX]+", "", line).strip()
                for line in handle
                if line.strip()
            )
    else:
        ancient_text = "古文資料不存在。"

    wiki_content_file = os.path.join(
        YIJING_WIKI_GUA_CLEANED_PATH,
        f"yijing卦名維基文獻第{gua_number}條{safe_filename(title)}粗掃.txt",
    )
    if os.path.isfile(wiki_content_file):
        with open(wiki_content_file, "r", encoding="utf-8") as handle:
            wiki_lines = [line.strip() for line in handle if line.strip()]
        wiki_content = "\n".join(wiki_lines[1:])
    else:
        wiki_content = "維基百科資料不存在或尚未處理。"

    return {
        "title": title,
        "gua_number": gua_number,
        "ancient_text": ancient_text,
        "wiki_content": wiki_content,
        "external_links": [
            {"name": "Google 搜尋", "url": f"https://www.google.com/search?q={quote_plus(f'易經 {title}')}"},
            {"name": "百度搜尋", "url": f"https://www.baidu.com/s?wd={quote_plus(f'易经 {title}')}"},
            {"name": "維基百科", "url": f"https://zh.wikipedia.org/wiki/{quote(title, safe='')}"},
        ],
    }


@gua_bp.get("/<int:gua_number>")
def gua_page(gua_number: int):
    catalog = build_content_catalog()
    entry = catalog.find("gua", str(gua_number))
    if entry is None:
        abort(404)
    previous_entry, next_entry = catalog.adjacent("gua", entry.key)
    return render_template(
        "gua_page.html",
        gua_data=_load_gua_data(gua_number, entry.title),
        previous_entry=previous_entry,
        next_entry=next_entry,
        site_title="易經研讀室",
    )
```

Remove the broad `try` that converts invalid identifiers to an HTTP 200 page. `_load_gua_data()` keeps safe, section-specific fallback text for absent ancient and wiki files, while normal Jinja autoescaping continues to protect file content.

- [ ] **Step 5: Make available-case lookup use the canonical input directory**

Replace the current fengshui route body with catalog status validation plus the existing traversal-safe resolver:

```python
from .config import YIJING_ANCIENT_TEXT_PATH, YIJING_INPUT_PATH, YIJING_WIKI_GUA_CLEANED_PATH


@fengshui_bp.get("/case/<path:case_filename>")
def fengshui_case_page(case_filename: str):
    key = case_filename.removesuffix(".txt")
    entry = build_content_catalog().find("fengshui_case", key)
    if entry is None or not entry.available:
        abort(404)
    try:
        case_file = resolve_existing_child(YIJING_INPUT_PATH, key, suffixes=(".txt", ""))
    except (FileNotFoundError, ValueError):
        abort(404)
    case_data = {"title": case_file.stem, "content": case_file.read_text(encoding="utf-8")}
    return render_template(
        "fengshui_case_page.html",
        case_data=case_data,
        site_title="易經研讀室",
    )
```

- [ ] **Step 6: Run focused route and escaping tests**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py::test_gua_route_returns_404_outside_catalog tests/test_flask_app.py::test_all_64_catalog_gua_routes_are_readable tests/test_flask_app.py::test_fengshui_route_reads_input_directory_and_missing_is_404 tests/test_flask_app.py::test_file_content_is_html_escaped -q
```

Expected: all four tests pass, including the complete 64-route sweep.

- [ ] **Step 7: Commit route semantics**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/page_generator.py tests/conftest.py tests/test_flask_app.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "fix: make content availability authoritative"
```

Expected staged files: exactly the three paths in the `git add` command.

---

### Task 3: Shared Editorial Home and Progressive Search

**Files:**
- Create: `python/src/templates/base.html`
- Create: `python/src/templates/workspace.html`
- Create: `python/src/static/catalog.js`
- Modify: `python/src/main.py:1-207`
- Replace: `python/src/templates/index.html`
- Replace: `python/src/static/style.css`
- Modify: `tests/test_flask_app.py`
- Modify: `tests/test_repository_layout.py`

**Interfaces:**
- Consumes: `build_content_catalog()` and `ContentCatalog` count/filter methods.
- Produces template context: `catalog`, `gua_entries`, `slide_entries`, `case_entries`, and `catalog_warnings`.
- Produces a provisional `GET /workspace` page so the shared navigation is valid before processing orchestration is replaced in Task 5.
- Produces stable DOM contract for `catalog.js`: `[data-catalog-search]`, `[data-catalog-filter]`, `[data-catalog-entry]`, `data-kind`, `data-search`, `[data-catalog-count]`, and `[data-catalog-empty]`.

- [ ] **Step 1: Write failing homepage catalog and fallback tests**

Add to `tests/test_flask_app.py`:

```python
def test_index_renders_catalog_counts_and_unavailable_cases(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    inputs = data / "易經輸入端資料夾"
    (inputs / "易經個案列表.txt").write_text("易經個案001\n易經個案002\n", encoding="utf-8")
    (inputs / "易經個案001.txt").write_text("內容\n", encoding="utf-8")

    html = app.test_client().get("/").get_data(as_text=True)

    assert "2" in html
    assert "3" in html
    assert "1 / 2" in html
    assert 'data-kind="gua"' in html
    assert 'data-search="第 1 卦 1 乾 六十四卦 gua"' in html
    assert "易經個案002" in html
    assert "缺少內容檔" in html
    missing_card = html.split("易經個案002", 1)[1].split("</article>", 1)[0]
    assert "href=" not in missing_card


def test_index_survives_missing_titles_with_workspace_recovery(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "尚未找到卦名資料" in html
    assert 'href="/workspace"' in html


def test_index_renders_without_a_processing_form(app_factory):
    app, _ = app_factory()
    html = app.test_client().get("/").get_data(as_text=True)
    assert 'data-catalog-search' in html
    assert 'name="_csrf_token"' not in html
    assert '/process_interaction' not in html


def test_workspace_shell_is_reachable(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/workspace")
    assert response.status_code == 200
    assert "資料工作台" in response.get_data(as_text=True)
```

Replace `test_index_uses_existing_static_assets_and_csrf_token` in `tests/test_repository_layout.py` with:

```python
def test_index_uses_catalog_assets_and_has_no_processing_form():
    content = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    assert "data-catalog-search" in content
    assert "data-catalog-entry" in content
    assert "filename='catalog.js'" in content
    assert "process_interaction" not in content
    assert 'name="_csrf_token"' not in content
```

- [ ] **Step 2: Run the new homepage tests and verify the old page fails**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py::test_index_renders_catalog_counts_and_unavailable_cases tests/test_flask_app.py::test_index_survives_missing_titles_with_workspace_recovery tests/test_flask_app.py::test_index_renders_without_a_processing_form tests/test_flask_app.py::test_workspace_shell_is_reachable tests/test_repository_layout.py::test_index_uses_catalog_assets_and_has_no_processing_form -q
```

Expected: failures show the current index still builds separate lists and contains the processing form.

- [ ] **Step 3: Create the shared non-slide page frame**

Create `python/src/templates/base.html` with semantic landmarks and overridable blocks:

```html
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}易經研讀室{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  {% block head %}{% endblock %}
</head>
<body>
  <a class="skip-link" href="#main-content">跳至主要內容</a>
  <header class="site-header">
    <a class="site-brand" href="{{ url_for('index') }}">易經研讀室</a>
    <nav aria-label="主要導覽">
      <a href="{{ url_for('index') }}#guas">六十四卦</a>
      <a href="{{ url_for('index') }}#slides">投影片</a>
      <a href="{{ url_for('index') }}#cases">風水個案</a>
      <a href="{{ url_for('workspace') }}">資料工作台</a>
    </nav>
  </header>
  <main id="main-content">{% block content %}{% endblock %}</main>
  <footer class="site-footer">© 2026 易經研讀室</footer>
  {% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Make the home route catalog-driven**

Replace separate title/list file reading in `main.py` with:

```python
from .content_catalog import build_content_catalog


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
```

Remove processing flash lookup and all direct filesystem list assembly from `index()`.

Add a provisional read-only workspace endpoint so the new shared navigation never points at a missing route during this independently testable task:

```python
@app.get("/workspace")
def workspace():
    return render_template("workspace.html", processing_results=[])
```

- [ ] **Step 5: Replace the home template with the approved hierarchy**

Make `index.html` extend `base.html`. Render the hero search, statistics, type filters, gua cards, slide cards, case rows, warnings, and workspace callout. The central repeated item contract must follow this exact pattern:

```html
<article class="catalog-card"
         data-catalog-entry
         data-kind="{{ entry.kind }}"
         data-search="{{ entry.search_text }}">
  {% if entry.available %}
    <a class="catalog-card__link" href="{{ entry.url }}">
        <span class="catalog-card__meta">
          {% if entry.kind == "gua" %}第 {{ "%02d"|format(entry.number) }} 卦
          {% elif entry.kind == "slides" %}投影片講座
          {% else %}風水個案{% endif %}
        </span>
      <h3>{{ entry.title }}</h3>
    </a>
  {% else %}
    <div class="catalog-card__unavailable" aria-disabled="true">
      <h3>{{ entry.title }}</h3>
      <span class="status status--missing">{{ entry.unavailable_reason }}</span>
    </div>
  {% endif %}
</article>
```

Include `1 / 10` using `catalog.available_count('fengshui_case')` and `catalog.total_count('fengshui_case')`.

Create the initial `workspace.html` shell so the navigation destination is usable before Task 5 adds the processing form:

```html
{% extends "base.html" %}
{% block title %}資料工作台｜易經研讀室{% endblock %}
{% block content %}
<section class="page-intro workspace-intro">
  <p class="eyebrow">資料維護</p>
  <h1>資料工作台</h1>
  <p>集中管理本機資料與維基資料處理作業。</p>
</section>
{% endblock %}
```

- [ ] **Step 6: Implement client-only search and filtering**

Create `python/src/static/catalog.js`:

```javascript
"use strict";

const searchInput = document.querySelector("[data-catalog-search]");
const filters = [...document.querySelectorAll("[data-catalog-filter]")];
const entries = [...document.querySelectorAll("[data-catalog-entry]")];
const count = document.querySelector("[data-catalog-count]");
const empty = document.querySelector("[data-catalog-empty]");
let activeKind = "all";

function normalize(value) {
  return value.trim().replace(/\s+/g, " ").toLocaleLowerCase("zh-Hant");
}

function applyCatalogFilters() {
  const query = normalize(searchInput?.value ?? "");
  let visible = 0;
  for (const entry of entries) {
    const kindMatches = activeKind === "all" || entry.dataset.kind === activeKind;
    const textMatches = normalize(entry.dataset.search ?? "").includes(query);
    entry.hidden = !(kindMatches && textMatches);
    if (!entry.hidden) visible += 1;
  }
  if (count) count.textContent = String(visible);
  if (empty) empty.hidden = visible !== 0;
}

searchInput?.addEventListener("input", applyCatalogFilters);
for (const filter of filters) {
  filter.addEventListener("click", () => {
    activeKind = filter.dataset.catalogFilter ?? "all";
    for (const candidate of filters) {
      candidate.setAttribute("aria-pressed", String(candidate === filter));
    }
    applyCatalogFilters();
  });
}
```

Load it with `defer` from the index template's `scripts` block.

- [ ] **Step 7: Build the editorial CSS foundation and responsive home components**

Replace `style.css` with design tokens and component rules beginning with:

```css
:root {
  color-scheme: light;
  --paper: #f5f0e7;
  --surface: #fffdf8;
  --ink: #292722;
  --ink-green: #203b35;
  --brass: #b89455;
  --muted: #6f6a61;
  --border: #ded2bf;
  --danger: #8b2f2f;
  --radius-sm: .65rem;
  --radius-lg: 1.15rem;
  --content-width: 74rem;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; color: var(--ink); background: var(--paper); }
a:focus-visible, button:focus-visible, input:focus-visible {
  outline: 3px solid var(--brass);
  outline-offset: 3px;
}
.catalog-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
[hidden] { display: none !important; }

@media (max-width: 48rem) {
  .site-header, .hero-grid { grid-template-columns: 1fr; }
  .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
```

Add explicit rules for skip link, header/nav, hero, search, statistic cards, filter buttons, catalog cards, unavailable state, warning, workspace callout, footer, and a `max-width: 100%` rule for media. Test at 320 CSS pixels without horizontal overflow.

- [ ] **Step 8: Run home and repository-layout tests**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_content_catalog.py tests/test_flask_app.py tests/test_repository_layout.py -q
```

Expected: catalog/home/structure tests pass; unrelated tests remain green.

- [ ] **Step 9: Commit the shared frame and home experience**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/main.py python/src/templates/base.html python/src/templates/workspace.html python/src/templates/index.html python/src/static/style.css python/src/static/catalog.js tests/test_flask_app.py tests/test_repository_layout.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "feat: build searchable editorial catalog"
```

Expected staged files: exactly the eight paths in the `git add` command.

---

### Task 4: Shared Reading Pages and Friendly Errors

**Files:**
- Create: `python/src/templates/error.html`
- Modify: `python/src/main.py`
- Modify: `python/src/templates/gua_page.html`
- Modify: `python/src/templates/fengshui_case_page.html`
- Modify: `python/src/static/style.css`
- Modify: `tests/test_flask_app.py`
- Modify: `tests/test_repository_layout.py`

**Interfaces:**
- Consumes: `previous_entry` and `next_entry` from the gua route; `base.html` blocks.
- Produces: `error.html` context `error_code`, `error_title`, `error_message`; registered Flask 404 handler returning status 404.
- Produces stable in-page anchors: `#ancient-text`, `#wiki-reference`, and `#external-links`.

- [ ] **Step 1: Write failing reading-navigation and friendly-404 tests**

Add to `tests/test_flask_app.py`:

```python
def test_gua_page_has_sections_and_next_navigation(app_factory):
    app, data = app_factory()
    _seed_two_guas(data)
    html = app.test_client().get("/gua/1").get_data(as_text=True)

    assert 'id="ancient-text"' in html
    assert 'id="wiki-reference"' in html
    assert 'id="external-links"' in html
    assert 'href="/gua/2"' in html
    assert "下一卦：坤" in html
    assert "1 / 2" in html


def test_missing_content_uses_friendly_404_template(app_factory):
    app, _ = app_factory()
    response = app.test_client().get("/fengshui/case/不存在")

    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "找不到內容" in html
    assert 'href="/"' in html
```

Update `tests/test_repository_layout.py` so `base.html` and `error.html` are required templates, and assert that `gua_page.html` and `fengshui_case_page.html` both contain `{% extends "base.html" %}` and contain no `<style>` tag.

- [ ] **Step 2: Run the reading-page tests and verify markup failures**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py::test_gua_page_has_sections_and_next_navigation tests/test_flask_app.py::test_missing_content_uses_friendly_404_template tests/test_repository_layout.py -q
```

Expected: tests fail because current detail templates are standalone and Flask uses the default 404 page.

- [ ] **Step 3: Register the friendly 404 page**

Add to `create_app()` after blueprint registration:

```python
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
```

Create `error.html` extending `base.html`, with the code, title, message, and a home link. Do not echo raw exception text.

- [ ] **Step 4: Replace gua and case templates with the shared reading frame**

The gua template must use this semantic skeleton:

```html
{% extends "base.html" %}
{% block title %}{{ gua_data.title }}｜易經研讀室{% endblock %}
{% block content %}
<article class="reading-page">
  <nav class="breadcrumbs" aria-label="麵包屑"><a href="{{ url_for('index') }}">典藏首頁</a> / 六十四卦 / {{ gua_data.title }}</nav>
  <header class="reading-header">
    <p class="eyebrow">第 {{ "%02d"|format(gua_data.gua_number) }} 卦</p>
    <h1>{{ gua_data.title }}</h1>
  </header>
  <nav class="section-nav" aria-label="本頁段落">
    <a href="#ancient-text">古文原文</a>
    <a href="#wiki-reference">維基參考</a>
    <a href="#external-links">外部連結</a>
  </nav>
  <section id="ancient-text"><h2>古文原文</h2><div class="prose">{{ gua_data.ancient_text }}</div></section>
  <section id="wiki-reference"><h2>維基百科參考資料</h2><div class="prose">{{ gua_data.wiki_content }}</div></section>
  <section id="external-links">
    <h2>外部參考連結</h2>
    <ul class="external-links">
      {% for link in gua_data.external_links %}
        <li><a href="{{ link.url }}" target="_blank" rel="noopener noreferrer">{{ link.name }}－{{ gua_data.title }}</a></li>
      {% endfor %}
    </ul>
  </section>
  <nav class="reading-pager" aria-label="卦序導覽">
    <span>{% if previous_entry %}<a href="{{ previous_entry.url }}">← 上一卦：{{ previous_entry.title }}</a>{% endif %}</span>
    <a href="{{ url_for('index') }}#guas">{{ gua_data.gua_number }} / {{ catalog_size }}</a>
    <span>{% if next_entry %}<a href="{{ next_entry.url }}">下一卦：{{ next_entry.title }} →</a>{% endif %}</span>
  </nav>
</article>
{% endblock %}
```

Add `catalog_size=catalog.total_count("gua")` in the gua route context. Make `fengshui_case_page.html` use the same breadcrumbs, reading header, and `.prose` content without a pager.

- [ ] **Step 5: Add reading, prose, breadcrumb, pager, and error styles**

Append focused rules to `style.css`: set `.reading-page` to `max-width: 52rem`, set `.prose` to `white-space: pre-wrap`, `overflow-wrap: anywhere`, and `line-height: 1.9`, make `.reading-pager` a three-column grid on desktop and one column below 48rem, and style `.error-page` with visible error code and home action. Keep all text selectable.

- [ ] **Step 6: Run detail-page, escaping, and structure tests**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py::test_gua_page_has_sections_and_next_navigation tests/test_flask_app.py::test_missing_content_uses_friendly_404_template tests/test_flask_app.py::test_file_content_is_html_escaped tests/test_repository_layout.py -q
```

Expected: all focused tests pass.

- [ ] **Step 7: Commit shared reading pages**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/main.py python/src/templates/error.html python/src/templates/gua_page.html python/src/templates/fengshui_case_page.html python/src/static/style.css tests/test_flask_app.py tests/test_repository_layout.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "feat: unify content reading pages"
```

Expected staged files: exactly the seven paths in the `git add` command.

---

### Task 5: Structured Processing Workspace

**Files:**
- Create: `python/src/processing.py`
- Replace: `python/src/templates/workspace.html`
- Create: `python/src/static/workspace.js`
- Create: `tests/test_processing.py`
- Modify: `python/src/main.py:1-275`
- Modify: `python/src/static/style.css`
- Modify: `tests/test_flask_app.py`
- Modify: `tests/test_repository_layout.py`

**Interfaces:**
- Produces `ProcessingSelection` with seven boolean step fields plus `custom_topic_start` and `custom_topic_end`.
- Produces `ProcessingStepResult(name: str, status: Literal['success', 'warning', 'error'], message: str)`.
- Produces `run_processing(selection: ProcessingSelection) -> tuple[ProcessingStepResult, ...]`.
- Replaces the provisional `GET /workspace` handler and produces `POST /workspace/process`; old `POST /process_interaction` must return 404.

- [ ] **Step 1: Write failing processing orchestration tests**

Create `tests/test_processing.py`:

```python
from src.processing import ProcessingSelection, run_processing


def test_empty_selection_is_fail_safe():
    results = run_processing(ProcessingSelection())

    assert [(result.status, result.message) for result in results] == [
        ("warning", "未選擇任何操作。")
    ]


def test_processing_reports_each_selected_step_and_continues(monkeypatch):
    calls = []

    def fail_prepare(reset=False):
        calls.append(("prepare", reset))
        raise OSError("disk unavailable")

    def succeed_format():
        calls.append(("format",))

    monkeypatch.setattr("src.processing.prepare_environment", fail_prepare)
    monkeypatch.setattr("src.processing.format_basic_data_files", succeed_format)

    results = run_processing(
        ProcessingSelection(run_prepare_env=True, run_format_basic=True)
    )

    assert calls == [("prepare", False), ("format",)]
    assert [result.status for result in results] == ["error", "success"]
    assert results[0].name == "環境準備"
    assert results[1].name == "基本資料格式化"
```

- [ ] **Step 2: Run processing tests and verify the module is missing**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_processing.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'src.processing'`.

- [ ] **Step 3: Move processing orchestration into immutable types**

Create `python/src/processing.py` with the existing imports and these types:

```python
from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Callable, Literal

from .config import YIJING_ANCIENT_TEXT_PATH
from .data_processor import (
    append_ancient_texts_to_compilation,
    format_basic_data_files,
    generate_yijing_metadata_and_split_guas,
    prepare_environment,
    process_yijing_raw_text,
)
from .wiki_handler import process_custom_topics_wiki, process_yijing_guas_wiki

logger = logging.getLogger(__name__)
ProcessingStatus = Literal["success", "warning", "error"]


@dataclass(frozen=True, slots=True)
class ProcessingSelection:
    run_prepare_env: bool = False
    run_format_basic: bool = False
    run_process_raw: bool = False
    run_gen_meta: bool = False
    run_append_ancient: bool = False
    run_custom_wiki: bool = False
    run_guas_wiki: bool = False
    custom_topic_start: int = 1
    custom_topic_end: int = 1

    def any_selected(self) -> bool:
        return any((
            self.run_prepare_env,
            self.run_format_basic,
            self.run_process_raw,
            self.run_gen_meta,
            self.run_append_ancient,
            self.run_custom_wiki,
            self.run_guas_wiki,
        ))


@dataclass(frozen=True, slots=True)
class ProcessingStepResult:
    name: str
    status: ProcessingStatus
    message: str
```

Implement `run_processing()` in the same order as the current `initialize_all_data()`. Wrap each selected operation separately, log exceptions, and append an error result so later independent selections continue. Preserve the metadata and append prerequisites exactly:

```python
def _attempt(
    name: str,
    action: Callable[[], bool | None],
    success: str,
    failure: str,
) -> ProcessingStepResult:
    try:
        outcome = action()
    except Exception:
        logger.exception("Processing step failed: %s", name)
        return ProcessingStepResult(name, "error", f"{name}失敗，請查看伺服器紀錄。")
    status: ProcessingStatus = "success" if outcome is not False else "error"
    return ProcessingStepResult(name, status, success if status == "success" else failure)


def run_processing(selection: ProcessingSelection) -> tuple[ProcessingStepResult, ...]:
    if not selection.any_selected():
        return (ProcessingStepResult("選擇操作", "warning", "未選擇任何操作。"),)
    results: list[ProcessingStepResult] = []
    if selection.run_prepare_env:
        results.append(
            _attempt(
                "環境準備",
                lambda: prepare_environment(reset=False),
                "環境準備完成，既有檔案已保留。",
                "環境準備未完成。",
            )
        )
    if selection.run_format_basic:
        results.append(
            _attempt(
                "基本資料格式化",
                format_basic_data_files,
                "基本資料檔案格式化完成。",
                "基本資料檔案格式化失敗。",
            )
        )

    raw_succeeded = False
    if selection.run_process_raw:
        raw_result = _attempt(
            "易經原文處理",
            process_yijing_raw_text,
            "易經原始文字檔處理完成。",
            "易經原始文字檔處理失敗。",
        )
        results.append(raw_result)
        raw_succeeded = raw_result.status == "success"

    metadata_succeeded = False
    if selection.run_gen_meta:
        processed_path = os.path.join(
            YIJING_ANCIENT_TEXT_PATH,
            "yijing每卦到空列分隔全文文本有分斷點.txt",
        )
        if raw_succeeded or os.path.exists(processed_path):
            metadata_result = _attempt(
                "易經元數據",
                generate_yijing_metadata_and_split_guas,
                "易經元數據產生並分割卦文完成。",
                "易經元數據產生或分割卦文失敗。",
            )
            results.append(metadata_result)
            metadata_succeeded = metadata_result.status == "success"
        else:
            results.append(
                ProcessingStepResult(
                    "易經元數據",
                    "warning",
                    "未產生易經元數據，因處理後的原始文字檔不存在。",
                )
            )

    if selection.run_append_ancient:
        titles_path = os.path.join(YIJING_ANCIENT_TEXT_PATH, "yijing標題.txt")
        if metadata_succeeded or os.path.exists(titles_path):
            results.append(
                _attempt(
                    "易經古文彙編",
                    append_ancient_texts_to_compilation,
                    "易經古文已寫入彙編。",
                    "易經古文寫入彙編失敗。",
                )
            )
        else:
            results.append(
                ProcessingStepResult(
                    "易經古文彙編",
                    "warning",
                    "未寫入易經古文，因標題資料不存在。",
                )
            )

    if selection.run_custom_wiki:
        results.append(
            _attempt(
                "自選主題維基資料",
                lambda: process_custom_topics_wiki(
                    begin_line=selection.custom_topic_start,
                    end_line=selection.custom_topic_end,
                ),
                f"自選主題維基百科資料處理完成（第 {selection.custom_topic_start} 至 {selection.custom_topic_end} 行）。",
                "自選主題維基百科資料未完成，請查看伺服器紀錄。",
            )
        )

    if selection.run_guas_wiki:
        results.append(
            _attempt(
                "六十四卦維基資料",
                process_yijing_guas_wiki,
                "易經卦名維基百科資料處理完成。",
                "易經卦名維基百科資料未完成，請查看伺服器紀錄。",
            )
        )
    return tuple(results)
```

- [ ] **Step 4: Verify processing results and dependency warnings**

Extend `tests/test_processing.py` with explicit missing-prerequisite cases:

```python
def test_metadata_and_append_report_missing_prerequisites(monkeypatch, tmp_path):
    monkeypatch.setattr("src.processing.YIJING_ANCIENT_TEXT_PATH", str(tmp_path))
    results = run_processing(
        ProcessingSelection(run_gen_meta=True, run_append_ancient=True)
    )
    assert [result.status for result in results] == ["warning", "warning"]
    assert "處理後的原始文字檔不存在" in results[0].message
    assert "標題資料不存在" in results[1].message
```

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_processing.py -q
```

Expected: all processing tests pass.

- [ ] **Step 5: Write failing workspace route tests**

Update old form tests in `tests/test_flask_app.py` and add PRG/result assertions:

```python
def _csrf_from(html: bytes) -> str:
    import re
    match = re.search(rb'name="_csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1).decode("utf-8")


def test_workspace_requires_csrf_and_old_route_is_removed(app_factory):
    app, _ = app_factory()
    client = app.test_client()
    assert client.post("/workspace/process", data={}).status_code == 400
    assert client.post("/process_interaction", data={}).status_code == 404


def test_workspace_empty_submission_redirects_to_structured_warning(app_factory):
    app, _ = app_factory()
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={"_csrf_token": token, "custom_topic_start": "1", "custom_topic_end": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workspace")
    html = client.get("/workspace").get_data(as_text=True)
    assert "未選擇任何操作" in html
    assert 'data-result-status="warning"' in html


def test_workspace_selected_operation_uses_prg_and_renders_success(
    app_factory, monkeypatch
):
    app, _ = app_factory()
    import src.main as main

    selections = []

    def fake_run(selection):
        selections.append(selection)
        return (
            main.ProcessingStepResult(
                "環境準備", "success", "環境準備完成，既有檔案已保留。"
            ),
        )

    monkeypatch.setattr(main, "run_processing", fake_run)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_prepare_environment": "true",
            "custom_topic_start": "1",
            "custom_topic_end": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert selections[0].run_prepare_env is True
    html = response.get_data(as_text=True)
    assert "環境準備完成" in html
    assert 'data-result-status="success"' in html


def test_workspace_invalid_range_is_reported_without_running(app_factory, monkeypatch):
    app, _ = app_factory()
    import src.main as main

    def fail_if_called(_selection):
        raise AssertionError("run_processing must not be called for an invalid range")

    monkeypatch.setattr(main, "run_processing", fail_if_called)
    client = app.test_client()
    token = _csrf_from(client.get("/workspace").data)
    response = client.post(
        "/workspace/process",
        data={
            "_csrf_token": token,
            "run_process_custom_wiki": "true",
            "custom_topic_start": "10",
            "custom_topic_end": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "輸入資料有誤" in response.get_data(as_text=True)
    assert 'data-result-status="error"' in response.get_data(as_text=True)
```

- [ ] **Step 6: Replace old processing routes with workspace PRG**

Remove `initialize_all_data`, the home form route, and their processing-function imports from `main.py`. Import `asdict`, `ProcessingSelection`, and `run_processing`, replace the provisional workspace handler, then add:

```python
from dataclasses import asdict

from .processing import ProcessingSelection, ProcessingStepResult, run_processing


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


@app.get("/workspace")
def workspace():
    flashed = get_flashed_messages(category_filter=["processing_report"])
    return render_template("workspace.html", processing_results=flashed[-1] if flashed else [])


@app.post("/workspace/process")
def process_workspace():
    try:
        results = run_processing(_processing_selection_from_request())
    except ValueError as exc:
        results = (ProcessingStepResult("輸入驗證", "error", f"輸入資料有誤：{exc}"),)
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
```

In `tests/conftest.py`, extend the imports and reload order exactly as follows so every route test uses temporary data paths rather than module state from an earlier test:

```python
import src.processing as processing
import src.main as main

for module in (
    content_catalog,
    data_processor,
    wiki_handler,
    processing,
    slide_generator,
    page_generator,
    main,
):
    importlib.reload(module)
```

- [ ] **Step 7: Create grouped workspace markup and guarded enhancement**

Replace the workspace shell with `workspace.html` extending `base.html`. Keep the submit button enabled in server-rendered HTML so the form remains usable without JavaScript; the enhancement script will apply the empty-selection guard after load:

```html
{% extends "base.html" %}
{% block title %}資料工作台｜易經研讀室{% endblock %}
{% block content %}
<section class="page-intro workspace-intro">
  <p class="eyebrow">資料維護</p>
  <h1>資料工作台</h1>
  <p>只執行明確勾選的操作；網路操作可能需要較長時間。</p>
</section>

{% if processing_results %}
<section class="processing-report" aria-labelledby="processing-report-title">
  <h2 id="processing-report-title">本次處理結果</h2>
  <ul>
    {% for result in processing_results %}
    <li class="processing-result processing-result--{{ result.status }}"
        data-result-status="{{ result.status }}">
      <strong>{{ result.name }}</strong>
      <span>{{ result.message }}</span>
    </li>
    {% endfor %}
  </ul>
</section>
{% endif %}

<form class="workspace-form" method="post" action="{{ url_for('process_workspace') }}" data-workspace-form>
  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
  <div class="workspace-layout">
    <fieldset class="operation-group">
      <legend>本機資料處理</legend>
      <label><input type="checkbox" name="run_prepare_environment" value="true" data-operation> 補齊缺少資料 <span class="impact-badge">保留既有檔</span></label>
      <label><input type="checkbox" name="run_format_basic_data" value="true" data-operation> 格式化基本資料 <span class="impact-badge">寫入</span></label>
      <label><input type="checkbox" name="run_process_yijing_raw" value="true" data-operation> 處理易經原文 <span class="impact-badge">寫入</span></label>
      <label><input type="checkbox" name="run_generate_yijing_meta" value="true" data-operation> 產生易經元數據 <span class="impact-badge">寫入</span></label>
      <label><input type="checkbox" name="run_append_ancient_texts" value="true" data-operation> 寫入古文彙編 <span class="impact-badge">寫入</span></label>
    </fieldset>
    <fieldset class="operation-group">
      <legend>網路資料處理</legend>
      <label><input type="checkbox" name="run_process_custom_wiki" value="true" data-operation data-custom-wiki> 自選主題維基 <span class="impact-badge">需要網路／大量請求</span></label>
      <fieldset class="range-fields" data-custom-range>
        <legend>自選主題範圍</legend>
        <label>起始行 <input type="number" name="custom_topic_start" value="1" min="1" max="10000"></label>
        <label>結束行 <input type="number" name="custom_topic_end" value="1" min="1" max="10000"></label>
      </fieldset>
      <label><input type="checkbox" name="run_process_guas_wiki" value="true" data-operation> 六十四卦維基 <span class="impact-badge">需要網路／大量請求</span></label>
    </fieldset>
  </div>
  <button class="primary-action" type="submit" data-workspace-submit>執行選取操作</button>
</form>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', filename='workspace.js') }}" defer></script>{% endblock %}
```

Create `workspace.js` with the exact progressive-enhancement behavior:

```javascript
"use strict";

const form = document.querySelector("[data-workspace-form]");
const operations = [...document.querySelectorAll("[data-operation]")];
const customWiki = document.querySelector("[data-custom-wiki]");
const customRange = document.querySelector("[data-custom-range]");
const submit = document.querySelector("[data-workspace-submit]");

function syncWorkspaceState() {
  if (customRange) customRange.disabled = !customWiki?.checked;
  if (submit) submit.disabled = !operations.some(operation => operation.checked);
}

for (const operation of operations) {
  operation.addEventListener("change", syncWorkspaceState);
}
form?.addEventListener("submit", () => {
  if (submit) {
    submit.disabled = true;
    submit.textContent = "處理中…";
  }
});
syncWorkspaceState();
```

Add `.workspace-layout`, `.operation-group`, `.impact-badge`, and `.processing-result--success|warning|error` rules to `style.css`, always pairing color with visible status text.

- [ ] **Step 8: Update repository guardrails and run workspace tests**

Update `tests/test_repository_layout.py` to require `workspace.html` and `workspace.js`, assert the workspace contains no `generate_all_outputs`, and assert `index.html` contains no form action. Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_processing.py tests/test_flask_app.py tests/test_repository_layout.py -q
```

Expected: processing, workspace, CSRF, old-route removal, and structure tests pass.

- [ ] **Step 9: Commit the structured workspace**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/processing.py python/src/main.py python/src/templates/workspace.html python/src/static/workspace.js python/src/static/style.css tests/test_processing.py tests/conftest.py tests/test_flask_app.py tests/test_repository_layout.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "feat: separate structured processing workspace"
```

Expected staged files: exactly the nine paths in the `git add` command.

---

### Task 6: Accessible impress.js Controls

**Files:**
- Create: `python/src/static/slides-controls.css`
- Create: `python/src/static/slides-controls.js`
- Modify: `python/src/templates/impress_slides_base.html`
- Modify: `python/src/templates/slides_yijing_guaci_moms_records.html`
- Modify: `tests/test_repository_layout.py`
- Modify: `tests/test_flask_app.py`

**Interfaces:**
- Consumes: global `impress()` API and `impress:stepenter` events emitted by existing `impress.js`.
- Produces DOM controls: `[data-slide-prev]`, `[data-slide-next]`, `[data-slide-progress]`, `[data-slide-help-toggle]`, and `[data-slide-help]`.
- Leaves all slide generator route names and `slides_data` records unchanged.

- [ ] **Step 1: Write failing slide-control structure tests**

Add to `tests/test_repository_layout.py`:

```python
def test_slide_base_has_accessible_controls_and_external_assets():
    content = (TEMPLATES / "impress_slides_base.html").read_text(encoding="utf-8")
    assert "data-slide-prev" in content
    assert "data-slide-next" in content
    assert "data-slide-progress" in content
    assert "data-slide-help-toggle" in content
    assert "filename='slides-controls.css'" in content
    assert "filename='slides-controls.js'" in content
    assert "impress().init()" not in content
```

Extend `test_tuanxiang_route_has_a_real_template` to assert `data-slide-progress`, `返回首頁`, and `slides-controls.js` occur in the response HTML.

- [ ] **Step 2: Run slide tests and verify controls are absent**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_repository_layout.py::test_slide_base_has_accessible_controls_and_external_assets tests/test_flask_app.py::test_tuanxiang_route_has_a_real_template -q
```

Expected: both tests fail on the current inline initialization-only base template.

- [ ] **Step 3: Add the fixed slide toolbar and help panel**

Modify `impress_slides_base.html` to load both new assets and place this markup before `#impress`. Preserve the existing `data-transition-duration`, slide coordinates, and content:

```html
<nav class="slide-toolbar" aria-label="投影片控制">
  <a class="slide-toolbar__home" href="{{ url_for('index') }}">返回首頁</a>
  <button type="button" data-slide-prev aria-label="上一張投影片">←</button>
  <output data-slide-progress aria-live="polite">1 / {{ slides_data|length }}</output>
  <button type="button" data-slide-next aria-label="下一張投影片">→</button>
  <button type="button" data-slide-help-toggle aria-expanded="false">操作說明</button>
</nav>
<aside class="slide-help" data-slide-help hidden>
  <h2>投影片操作</h2>
  <p>使用方向鍵或空白鍵移動；按 Esc 查看全覽；也可使用上方控制按鈕。</p>
</aside>
```

Remove inline `<script>impress().init();</script>`. Give image and video elements in `slides_yijing_guaci_moms_records.html` class `slide-media` and remove their inline sizing declarations.

- [ ] **Step 4: Implement impress controls and progress**

Create `slides-controls.js`:

```javascript
"use strict";

const deck = impress();
deck.init();
const slides = [...document.querySelectorAll("#impress .step.slide")];
const progress = document.querySelector("[data-slide-progress]");
const help = document.querySelector("[data-slide-help]");
const helpToggle = document.querySelector("[data-slide-help-toggle]");

function updateProgress(step) {
  const index = slides.indexOf(step);
  if (progress) progress.textContent = index < 0 ? "總覽" : `${index + 1} / ${slides.length}`;
}

document.querySelector("[data-slide-prev]")?.addEventListener("click", () => deck.prev());
document.querySelector("[data-slide-next]")?.addEventListener("click", () => deck.next());
document.addEventListener("impress:stepenter", event => updateProgress(event.target));
helpToggle?.addEventListener("click", () => {
  const opening = help?.hidden ?? false;
  if (help) help.hidden = !opening;
  helpToggle.setAttribute("aria-expanded", String(opening));
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && help && !help.hidden) {
    help.hidden = true;
    helpToggle?.setAttribute("aria-expanded", "false");
  }
});
updateProgress(document.querySelector("#impress .step.active") ?? slides[0]);
```

Create `slides-controls.css` with a high-contrast toolbar fixed at the top, minimum 44px button targets, a non-obscuring help panel, `.slide-media { max-width: 100%; max-height: 500px; display: block; margin: auto; }`, and:

```css
@media (prefers-reduced-motion: reduce) {
  #impress, #impress * { transition-duration: .01ms !important; animation-duration: .01ms !important; }
}
```

- [ ] **Step 5: Run slide route, structure, and asset tests**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_flask_app.py::test_tuanxiang_route_has_a_real_template tests/test_repository_layout.py -q
```

Expected: all focused slide and structure tests pass.

- [ ] **Step 6: Commit slide controls**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- python/src/templates/impress_slides_base.html python/src/templates/slides_yijing_guaci_moms_records.html python/src/static/slides-controls.css python/src/static/slides-controls.js tests/test_repository_layout.py tests/test_flask_app.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "feat: add accessible slide controls"
```

Expected staged files: exactly the six paths in the `git add` command.

---

### Task 7: Documentation, Ignore Rule, and Full-System Verification

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`
- Modify: `tests/test_repository_layout.py`

**Interfaces:**
- Consumes: final route and control names from Tasks 3-6.
- Produces: user-facing route/control documentation and a repository guardrail that keeps `.superpowers/` artifacts untracked.

- [ ] **Step 1: Write failing documentation and ignore-rule guards**

Add to `tests/test_repository_layout.py`:

```python
def test_docs_describe_reading_home_workspace_and_slide_controls():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "http://127.0.0.1:5003/" in readme
    assert "/workspace" in readme
    assert "標題搜尋" in readme
    assert "投影片控制" in readme


def test_visual_companion_artifacts_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".superpowers/" in ignore
```

- [ ] **Step 2: Run the documentation guards and verify they fail**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m pytest tests/test_repository_layout.py::test_docs_describe_reading_home_workspace_and_slide_controls tests/test_repository_layout.py::test_visual_companion_artifacts_are_ignored -q
```

Expected: both assertions fail before the documentation update.

- [ ] **Step 3: Update README and ignore visual-companion output**

In `README.md`, replace the old page description with explicit sections for:

- reading home at `http://127.0.0.1:5003/`
- title search and type filters
- missing-case status behavior
- processing workspace at `http://127.0.0.1:5003/workspace`
- safe grouped operations and removed all-operations shortcut
- slide toolbar, keyboard controls, progress, and return-home action

Append this exact entry under local artifacts in `.gitignore`:

```gitignore
.superpowers/
```

- [ ] **Step 4: Run full automated verification**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m compileall -q python/src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest -q
```

Expected: compile exits 0 and all tests pass with zero failures.

- [ ] **Step 5: Start the candidate on an unused test port and crawl local routes**

Start a hidden background process on port 5004 with `DAD_AUTO_INITIALIZE=0`, then verify the route set without writing data:

```powershell
$existing = Get-NetTCPConnection -LocalPort 5004 -State Listen -ErrorAction SilentlyContinue
if ($existing) { throw "Port 5004 is already in use; do not stop the existing process." }
$env:PYTHONPATH = 'python'
$env:DAD_PROJECT_ROOT = (Get-Location).Path
$env:DAD_SECRET_KEY = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
$env:DAD_HOST = '127.0.0.1'
$env:DAD_PORT = '5004'
$env:DAD_DEBUG = '0'
$env:DAD_AUTO_INITIALIZE = '0'
$candidate = Start-Process -FilePath 'python.exe' -ArgumentList '-m src.main' -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru
$pidPath = Join-Path $env:TEMP 'dad-reading-experience-5004.pid'
$candidate.Id | Set-Content -LiteralPath $pidPath
$ready = $false
foreach ($attempt in 1..20) {
    Start-Sleep -Milliseconds 500
    if ($candidate.HasExited) { break }
    try {
        $probe = Invoke-WebRequest -Uri 'http://127.0.0.1:5004/' -UseBasicParsing -TimeoutSec 2
        if ($probe.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
}
if (-not $ready) { throw "Candidate service did not become ready on port 5004." }

$okPaths = @(
    '/',
    '/workspace',
    '/slides/lecture_ancient',
    '/slides/lecture_guaci_moms_records',
    '/slides/lecture_tuanxiang',
    '/gua/1',
    '/gua/64',
    '/fengshui/case/%E6%98%93%E7%B6%93%E5%80%8B%E6%A1%88001'
)
foreach ($path in $okPaths) {
    $response = Invoke-WebRequest -Uri ("http://127.0.0.1:5004" + $path) -UseBasicParsing -TimeoutSec 15
    if ($response.StatusCode -ne 200) { throw "$path returned $($response.StatusCode)" }
}

$missingPaths = @(
    '/gua/65',
    '/fengshui/case/%E6%98%93%E7%B6%93%E5%80%8B%E6%A1%88002',
    '/process_interaction'
)
foreach ($path in $missingPaths) {
    $response = Invoke-WebRequest -Uri ("http://127.0.0.1:5004" + $path) -UseBasicParsing -SkipHttpErrorCheck -TimeoutSec 15
    if ($response.StatusCode -ne 404) { throw "$path returned $($response.StatusCode), expected 404" }
}
```

Expected: the candidate stays running for browser verification, all eight readable routes return 200, and all three removed or unavailable routes return 404.

- [ ] **Step 6: Perform browser verification at desktop and mobile widths**

Use the in-app Browser against `http://127.0.0.1:5004/` and verify these exact flows:

1. Search `乾`, then `第 64 卦`, and confirm each query leaves the matching gua entry.
2. Search `彖象` and confirm the matching slide entry; search `001` and confirm the matching case entry.
3. Search `完全不存在` and confirm the empty-results message, then clear search and confirm all entries return.
4. Choose `投影片` and confirm exactly three entries remain; switch among every type filter and back to `全部`.
5. Choose `風水個案`, confirm the summary shows `1 / 10`, `001` is a link, and `002` is disabled with `缺少內容檔`.
6. Open `/gua/1`, follow `下一卦：坤`, and return through the catalog anchor.
7. Open `/workspace`, confirm submit is disabled until one operation is selected, confirm the custom range enables only with its operation, then leave every operation unsubmitted to avoid data writes.
8. Open one slide deck, use next/previous, open and close help, verify the counter changes, and return home.
9. Check browser console errors: expected zero.
10. Check a desktop viewport near 1440×900 and a mobile viewport near 390×844: expected no horizontal overflow and all controls reachable by keyboard.

After the browser checks, reset the temporary viewport and stop only the recorded candidate process:

```powershell
$pidPath = Join-Path $env:TEMP 'dad-reading-experience-5004.pid'
$candidatePid = [int](Get-Content -LiteralPath $pidPath -Raw)
$candidateProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $candidatePid"
if (-not $candidateProcess -or $candidateProcess.CommandLine -notmatch '-m src\.main') {
    throw "Recorded PID does not identify the DAD candidate process."
}
Stop-Process -Id $candidatePid
Remove-Item -LiteralPath $pidPath
```

- [ ] **Step 7: Review the feature diff for generated-data leakage**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' status --short
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --check
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --stat 652b188..HEAD
```

Expected: user-owned `config_data` changes may remain visible but are unstaged and absent from the feature commit range. No whitespace errors are reported.

- [ ] **Step 8: Commit documentation and ignore rule**

Run:

```powershell
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' add -- README.md .gitignore tests/test_repository_layout.py
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' diff --cached --name-only
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' commit -m "docs: document refreshed DAD experience"
```

Expected staged files: exactly `README.md`, `.gitignore`, and `tests/test_repository_layout.py`.

- [ ] **Step 9: Re-run the release gate after the final commit**

Run:

```powershell
$env:PYTHONPATH = 'python'
python -m compileall -q python/src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest -q
git -c safe.directory='%(prefix)///192.168.68.68/node/dad' status --short
```

Expected: compile exits 0, every test passes, and only pre-existing user-owned generated-data changes are reported.
