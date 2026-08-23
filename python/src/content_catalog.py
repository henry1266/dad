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
