from dataclasses import FrozenInstanceError
import logging

import pytest

from src.processing import ProcessingSelection, ProcessingStepResult, run_processing


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


def test_metadata_and_append_report_missing_prerequisites(monkeypatch, tmp_path):
    monkeypatch.setattr("src.processing.YIJING_ANCIENT_TEXT_PATH", str(tmp_path))
    results = run_processing(
        ProcessingSelection(run_gen_meta=True, run_append_ancient=True)
    )

    assert [result.status for result in results] == ["warning", "warning"]
    assert "處理後的原始文字檔不存在" in results[0].message
    assert "標題資料不存在" in results[1].message


def test_all_seven_operations_run_once_in_order_and_forward_custom_range(monkeypatch):
    calls = []

    def record(name, outcome=True):
        def action(*args, **kwargs):
            calls.append((name, args, kwargs))
            return outcome

        return action

    monkeypatch.setattr("src.processing.prepare_environment", record("prepare"))
    monkeypatch.setattr("src.processing.format_basic_data_files", record("format"))
    monkeypatch.setattr("src.processing.process_yijing_raw_text", record("raw"))
    monkeypatch.setattr(
        "src.processing.generate_yijing_metadata_and_split_guas",
        record("metadata"),
    )
    monkeypatch.setattr(
        "src.processing.append_ancient_texts_to_compilation",
        record("append"),
    )
    monkeypatch.setattr(
        "src.processing.process_custom_topics_wiki",
        record("custom_wiki"),
    )
    monkeypatch.setattr(
        "src.processing.process_yijing_guas_wiki",
        record("guas_wiki"),
    )

    results = run_processing(
        ProcessingSelection(
            run_prepare_env=True,
            run_format_basic=True,
            run_process_raw=True,
            run_gen_meta=True,
            run_append_ancient=True,
            run_custom_wiki=True,
            run_guas_wiki=True,
            custom_topic_start=7,
            custom_topic_end=11,
        )
    )

    assert calls == [
        ("prepare", (), {"reset": False}),
        ("format", (), {}),
        ("raw", (), {}),
        ("metadata", (), {}),
        ("append", (), {}),
        ("custom_wiki", (), {"begin_line": 7, "end_line": 11}),
        ("guas_wiki", (), {}),
    ]
    assert isinstance(results, tuple)
    assert [result.name for result in results] == [
        "環境準備",
        "基本資料格式化",
        "易經原文處理",
        "易經元數據",
        "易經古文彙編",
        "自選主題維基資料",
        "六十四卦維基資料",
    ]
    assert [result.status for result in results] == ["success"] * 7


def test_network_operations_returning_false_report_errors(monkeypatch):
    monkeypatch.setattr(
        "src.processing.process_custom_topics_wiki",
        lambda **_kwargs: False,
    )
    monkeypatch.setattr("src.processing.process_yijing_guas_wiki", lambda: False)

    results = run_processing(
        ProcessingSelection(run_custom_wiki=True, run_guas_wiki=True)
    )

    assert [(result.name, result.status, result.message) for result in results] == [
        (
            "自選主題維基資料",
            "error",
            "自選主題維基百科資料未完成，請查看伺服器紀錄。",
        ),
        (
            "六十四卦維基資料",
            "error",
            "易經卦名維基百科資料未完成，請查看伺服器紀錄。",
        ),
    ]


def test_processing_exception_is_logged_without_exposing_details(
    monkeypatch, caplog
):
    private_detail = "private path C:/sensitive/source.txt"

    def fail_prepare(reset=False):
        raise OSError(private_detail)

    monkeypatch.setattr("src.processing.prepare_environment", fail_prepare)

    with caplog.at_level(logging.ERROR, logger="src.processing"):
        result = run_processing(ProcessingSelection(run_prepare_env=True))[0]

    assert result.status == "error"
    assert result.message == "環境準備失敗，請查看伺服器紀錄。"
    assert private_detail not in result.message
    assert any(
        record.getMessage() == "Processing step failed: 環境準備"
        and record.exc_info is not None
        for record in caplog.records
    )


def test_processing_values_are_immutable_slotted_and_results_are_tuples():
    selection = ProcessingSelection()
    result = ProcessingStepResult("選擇操作", "warning", "未選擇任何操作。")

    with pytest.raises(FrozenInstanceError):
        selection.run_prepare_env = True
    with pytest.raises(FrozenInstanceError):
        result.status = "success"

    assert not hasattr(selection, "__dict__")
    assert not hasattr(result, "__dict__")
    results = run_processing(selection)
    assert isinstance(results, tuple)
    assert [(item.name, item.status, item.message) for item in results] == [
        ("選擇操作", "warning", "未選擇任何操作。")
    ]
