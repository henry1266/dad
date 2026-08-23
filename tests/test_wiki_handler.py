from __future__ import annotations

from pathlib import Path

import src.wiki_handler as wiki


class FakeResponse:
    def __init__(self, html: str):
        self.text = html
        self.content = html.encode("utf-8")

    def raise_for_status(self):
        return None


def test_wikipedia_request_uses_https_encoded_topic_and_user_agent(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse('<main id="content"><p>正文</p></main>')

    monkeypatch.setattr(wiki.requests, "get", fake_get)
    assert wiki.get_wiki_content_basic("乾 卦/測試") == "正文"

    url, kwargs = calls[0]
    assert url == "https://zh.wikipedia.org/zh-tw/%E4%B9%BE%20%E5%8D%A6%2F%E6%B8%AC%E8%A9%A6"
    assert kwargs["headers"]["User-Agent"]
    assert kwargs["timeout"] == 15


def test_wikipedia_cleanup_removes_ui_elements_and_creates_parent(monkeypatch, tmp_path):
    html = '''
    <main id="content">
      <h1>標題<span class="mw-editsection">[編輯]</span></h1>
      <p>正文<sup class="reference">[1]</sup></p>
      <div class="toc"><p>目錄文字</p></div>
    </main>
    '''
    monkeypatch.setattr(wiki.requests, "get", lambda *a, **k: FakeResponse(html))
    output = tmp_path / "nested" / "cleaned.txt"

    result = wiki.get_wiki_content_basic("乾", cleaned_save_path=str(output))

    assert "[編輯]" not in result
    assert "[1]" not in result
    assert "目錄文字" not in result
    assert output.exists()


def test_safe_filename_removes_path_separators_and_control_characters():
    assert wiki.safe_filename("乾/坤\\測試\n") == "乾_坤_測試"

def test_custom_topics_updates_compilation_without_duplicates(monkeypatch, tmp_path):
    input_dir = tmp_path / "input"
    wiki_result = tmp_path / "wiki-result"
    wiki_temp = tmp_path / "wiki-temp"
    input_dir.mkdir()
    (input_dir / "易經自選專有名詞.txt").write_text("陰陽\n", encoding="utf-8")
    compilation = tmp_path / "book.txt"
    compilation.write_text("手動內容\n", encoding="utf-8")

    monkeypatch.setattr(wiki, "YIJING_INPUT_PATH", str(input_dir))
    monkeypatch.setattr(wiki, "YIJING_WIKI_RESULT_PATH", str(wiki_result))
    monkeypatch.setattr(wiki, "YIJING_WIKI_TEMP_PATH", str(wiki_temp))
    monkeypatch.setattr(wiki, "MAIN_COMPILATION_FILE", str(compilation))
    monkeypatch.setattr(wiki, "get_wiki_content_basic", lambda *a, **k: "陰陽內容")

    assert wiki.process_custom_topics_wiki(1, 1) is True
    assert wiki.process_custom_topics_wiki(1, 1) is True

    content = compilation.read_text(encoding="utf-8")
    assert content.startswith("手動內容")
    assert content.count("[[DAD:custom_topics_wiki:BEGIN]]") == 1
    assert content.count("陰陽內容") == 1
