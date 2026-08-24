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
        import src.processing as processing
        import src.slide_generator as slide_generator
        import src.page_generator as page_generator
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
        return main.create_app({"TESTING": True}), data

    return create
