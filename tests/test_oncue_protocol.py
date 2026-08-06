"""Tests for oncue:// deep-link protocol parsing."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from oncue.protocol import apply_url


@pytest.fixture
def mock_config():
    with patch("oncue.protocol.get_config") as get_cfg, patch(
        "oncue.protocol.set_config"
    ) as set_cfg:
        class _Cfg:
            oncue_token = ""
            web_url = ""
            rag_url = ""
            backend_url = ""
            provider = "groq"

            def save(self):
                pass

        cfg = _Cfg()
        get_cfg.return_value = cfg
        yield cfg, set_cfg


def test_apply_url_sets_all_connect_params(mock_config):
    cfg, set_cfg = mock_config
    url = (
        "oncue://connect?token=sk-test"
        "&web=https%3A%2F%2Fapp.example.com"
        "&rag=https%3A%2F%2Fdb.example.com%2Frag"
        "&backend=https%3A%2F%2Flitellm.example.com"
    )
    result = apply_url(url)
    assert result == "Connected to your OnCUE account"
    assert cfg.oncue_token == "sk-test"
    assert cfg.web_url == "https://app.example.com"
    assert cfg.rag_url == "https://db.example.com/rag"
    assert cfg.backend_url == "https://litellm.example.com"
    assert cfg.provider == "hosted"
    set_cfg.assert_called_once_with(cfg)


def test_apply_url_token_only(mock_config):
    cfg, _set_cfg = mock_config
    result = apply_url("oncue://connect?token=abc")
    assert result == "Connected to your OnCUE account"
    assert cfg.oncue_token == "abc"
    assert cfg.provider == "hosted"


def test_apply_url_missing_token_returns_none(mock_config):
    assert apply_url("oncue://connect?web=https://x.com") is None


def test_apply_url_wrong_scheme_returns_none(mock_config):
    assert apply_url("https://example.com") is None


def test_apply_url_wrong_action_returns_none(mock_config):
    assert apply_url("oncue://other?token=abc") is None
