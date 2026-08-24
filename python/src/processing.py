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
        return any(
            (
                self.run_prepare_env,
                self.run_format_basic,
                self.run_process_raw,
                self.run_gen_meta,
                self.run_append_ancient,
                self.run_custom_wiki,
                self.run_guas_wiki,
            )
        )


@dataclass(frozen=True, slots=True)
class ProcessingStepResult:
    name: str
    status: ProcessingStatus
    message: str


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
