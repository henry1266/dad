from __future__ import annotations

import importlib
from pathlib import Path


def test_default_paths_are_repository_relative(monkeypatch):
    monkeypatch.delenv("DAD_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("DAD_BASH_SOURCE_DIR", raising=False)
    monkeypatch.delenv("DAD_CONFIG_DATA_DIR", raising=False)

    import src.config as config
    config = importlib.reload(config)

    expected_root = Path(config.__file__).resolve().parents[2]
    assert Path(config.PROJECT_ROOT) == expected_root
    assert Path(config.BASH_SOURCE_DIR) == expected_root / "bash"
    assert Path(config.CONFIG_DATA_PATH) == expected_root / "config_data"


def test_environment_can_override_data_directories(monkeypatch, tmp_path):
    project_root = tmp_path / "project"
    bash_root = tmp_path / "source"
    data_root = tmp_path / "data"
    monkeypatch.setenv("DAD_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("DAD_BASH_SOURCE_DIR", str(bash_root))
    monkeypatch.setenv("DAD_CONFIG_DATA_DIR", str(data_root))

    import src.config as config
    config = importlib.reload(config)

    assert Path(config.PROJECT_ROOT) == project_root.resolve()
    assert Path(config.BASH_SOURCE_DIR) == bash_root.resolve()
    assert Path(config.CONFIG_DATA_PATH) == data_root.resolve()
