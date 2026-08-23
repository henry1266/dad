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


def test_metadata_and_append_report_missing_prerequisites(monkeypatch, tmp_path):
    monkeypatch.setattr("src.processing.YIJING_ANCIENT_TEXT_PATH", str(tmp_path))
    results = run_processing(
        ProcessingSelection(run_gen_meta=True, run_append_ancient=True)
    )

    assert [result.status for result in results] == ["warning", "warning"]
    assert "處理後的原始文字檔不存在" in results[0].message
    assert "標題資料不存在" in results[1].message
