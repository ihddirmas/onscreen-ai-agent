"""Desktop deep-link flow: website 'Open OnCUE' → oncue://connect → hosted mode."""
from __future__ import annotations

from pathlib import Path

import pytest

from oncue.config import get_config
from oncue.protocol import apply_url


@pytest.fixture()
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_file = tmp_path / "config.env"
    monkeypatch.setattr("oncue.config.CONFIG_FILE", cfg_file)
    monkeypatch.setattr("oncue.config.CONFIG_DIR", tmp_path)
    monkeypatch.setenv("DEFAULT_PROVIDER", "groq")
    import oncue.config as config_mod

    config_mod._current = None
    yield cfg_file
    config_mod._current = None


def test_connect_url_switches_to_hosted_mode(isolated_config: Path):
    url = (
        "oncue://connect?token=sk-test-key"
        "&web=https://app.example.com"
        "&rag=https://supabase.example.com/functions/v1/rag"
    )
    msg = apply_url(url)
    assert msg == "Connected to your OnCUE account"

    cfg = get_config()
    assert cfg.provider == "hosted"
    assert cfg.oncue_token == "sk-test-key"
    assert cfg.web_url == "https://app.example.com"
    assert cfg.rag_url == "https://supabase.example.com/functions/v1/rag"
    assert isolated_config.exists()
    assert "ONCUE_TOKEN=sk-test-key" in isolated_config.read_text()


def test_connect_url_without_token_is_ignored(isolated_config: Path):
    assert apply_url("oncue://connect?web=https://app.example.com") is None
    cfg = get_config()
    assert cfg.provider == "groq"
    assert cfg.oncue_token == ""


def test_non_connect_scheme_is_ignored(isolated_config: Path):
    assert apply_url("https://example.com") is None
