"""Shared fixtures for GUI tests.

These tests drive real PySide6 widgets through pytest-qt's `qtbot` — real
event loop, real signals, real Qt widget tree. The one thing that must never
be real is on-disk config: `Config.save()` writes to the user's actual
%APPDATA%/OnCUE/config.env, and `load_config()` also reads a repo-root
`.env` (which holds live API keys here) as a fallback. `isolated_config`
redirects both to a throwaway tmp_path for every test in this package.

`CONFIG_FILE` is a plain `Path`, not a lazily-resolved accessor — any module
that did `from oncue.config import CONFIG_FILE` (oncue.app does, to gate the
first-run onboarding dialog) captured that Path at *its own* import time, so
patching `oncue.config.CONFIG_FILE` alone doesn't reach it. Patch every such
bare-name import too, or a clean machine's onboarding dialog will pop a real
blocking modal during a test run.
"""
from __future__ import annotations

import pytest

import oncue.app as app_module
import oncue.config as config_module
from oncue.config import Config


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    config_dir = tmp_path / "OnCUE"
    config_file = config_dir / "config.env"
    monkeypatch.setattr(config_module, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(app_module, "CONFIG_FILE", config_file)
    monkeypatch.chdir(tmp_path)  # so load_config()'s relative ".env" lookup can't hit the repo's
    config_module._current = None
    config_module.set_config(Config())
    yield
    config_module._current = None
