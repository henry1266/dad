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


def test_catalog_caps_oversized_title_source_at_canonical_64_guas(tmp_path):
    ancient = tmp_path / "ancient"
    inputs = tmp_path / "inputs"
    ancient.mkdir()
    inputs.mkdir()
    (ancient / "yijing標題.txt").write_text(
        "\n".join(f"卦名{number:02d}" for number in range(1, 67)) + "\n",
        encoding="utf-8",
    )

    catalog = build_content_catalog(
        ancient_text_path=ancient,
        yijing_input_path=inputs,
    )

    assert catalog.total_count("gua") == 64
    assert catalog.find("gua", "64").title == "卦名64"
    assert catalog.find("gua", "65") is None
    previous, following = catalog.adjacent("gua", "64")
    assert previous.key == "63"
    assert following is None
