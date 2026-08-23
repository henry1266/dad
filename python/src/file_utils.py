# -*- coding: utf-8 -*-
"""Atomic, repeatable text-file update helpers."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def upsert_text_section(
    path: str | os.PathLike[str],
    section_name: str,
    content: str,
    *,
    initial_header: str | None = None,
) -> None:
    """Insert or replace a named section without duplicating previous output."""
    if not section_name or any(char in section_name for char in "\r\n[]"):
        raise ValueError("Invalid section name")

    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    if not existing and initial_header:
        existing = initial_header.rstrip() + "\n"

    begin = f"[[DAD:{section_name}:BEGIN]]"
    end = f"[[DAD:{section_name}:END]]"
    begin_index = existing.find(begin)
    end_index = existing.find(end)
    if (begin_index == -1) != (end_index == -1):
        raise ValueError(f"Incomplete markers for section {section_name}")
    if begin_index != -1 and end_index < begin_index:
        raise ValueError(f"Invalid marker order for section {section_name}")

    section = f"{begin}\n{content.rstrip()}\n{end}"
    if begin_index == -1:
        prefix = existing.rstrip()
        updated = f"{prefix}\n\n{section}\n" if prefix else f"{section}\n"
    else:
        after_end = end_index + len(end)
        updated = existing[:begin_index].rstrip() + "\n\n" + section
        suffix = existing[after_end:].strip("\n")
        if suffix:
            updated += "\n\n" + suffix
        updated += "\n"

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
