# -*- coding: utf-8 -*-
"""Small dependency-light helpers shared by Flask routes and generators."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from markupsafe import Markup, escape

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable without surprising fallbacks."""
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return default


def validate_range(
    start: int,
    end: int,
    *,
    minimum: int,
    maximum: int,
    max_span: int | None = None,
) -> tuple[int, int]:
    """Validate an inclusive numeric range and return it unchanged."""
    if start < minimum or end > maximum:
        raise ValueError(f"範圍必須介於 {minimum} 到 {maximum} 之間。")
    if end < start:
        raise ValueError("結束值不得小於起始值。")
    if max_span is not None and end - start + 1 > max_span:
        raise ValueError(f"一次最多可處理 {max_span} 筆資料。")
    return start, end


def resolve_existing_child(
    base_directory: str | os.PathLike[str],
    name: str,
    *,
    suffixes: Iterable[str] = ("",),
) -> Path:
    """Resolve an existing child while preventing traversal outside ``base``."""
    if not name or "\x00" in name:
        raise ValueError("檔名無效。")
    base = Path(base_directory).expanduser().resolve()
    for suffix in suffixes:
        candidate = (base / f"{name}{suffix}").resolve()
        try:
            candidate.relative_to(base)
        except ValueError as exc:
            raise ValueError("檔案路徑超出允許的資料夾。") from exc
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"找不到檔案：{name}")


def text_to_html(value: str) -> Markup:
    """Escape plain text and preserve its line breaks for controlled HTML use."""
    escaped_lines = [escape(line) for line in value.splitlines()]
    return Markup("<br>\n").join(escaped_lines)
