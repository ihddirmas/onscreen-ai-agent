import httpx
import pytest

from webapp.services import litellm as litellm_service


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


def test_mint_key_raises_without_litellm_url(monkeypatch):
    monkeypatch.delenv("LITELLM_URL", raising=False)
    with pytest.raises(RuntimeError, match="LITELLM_URL"):
        litellm_service.mint_key("user-1", "free")


def test_mint_key_returns_key_on_success(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse(200, {"key": "sk-user-abc"})

    monkeypatch.setattr(httpx, "post", fake_post)
    key = litellm_service.mint_key("user-1", "pro")
    assert key == "sk-user-abc"
    assert captured["url"] == "https://litellm.example.com/key/generate"
    assert captured["json"]["max_budget"] == 15.0
    assert captured["json"]["metadata"] == {"user_id": "user-1"}


def test_mint_key_free_tier_gets_only_groq_model(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}
    monkeypatch.setattr(
        httpx, "post",
        lambda url, headers, json, timeout: captured.update(json=json) or _FakeResponse(200, {"key": "sk-x"}),
    )
    litellm_service.mint_key("user-1", "free")
    assert captured["json"]["models"] == ["parakeet-groq"]


def test_mint_key_pro_tier_gets_all_hosted_models(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}
    monkeypatch.setattr(
        httpx, "post",
        lambda url, headers, json, timeout: captured.update(json=json) or _FakeResponse(200, {"key": "sk-x"}),
    )
    litellm_service.mint_key("user-1", "pro")
    assert captured["json"]["models"] == [
        "parakeet-groq",
        "parakeet-claude",
        "parakeet-gpt",
        "parakeet-gemini",
    ]


def test_mint_key_unknown_tier_defaults_to_free_models(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}
    monkeypatch.setattr(
        httpx, "post",
        lambda url, headers, json, timeout: captured.update(json=json) or _FakeResponse(200, {"key": "sk-x"}),
    )
    litellm_service.mint_key("user-1", "unknown-tier")
    assert captured["json"]["models"] == ["parakeet-groq"]


def test_update_key_budget_raises_without_litellm_url(monkeypatch):
    monkeypatch.delenv("LITELLM_URL", raising=False)
    with pytest.raises(RuntimeError, match="LITELLM_URL"):
        litellm_service.update_key_budget("sk-user-abc", "pro")


def test_update_key_budget_posts_to_key_update(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse(200, {})

    monkeypatch.setattr(httpx, "post", fake_post)
    litellm_service.update_key_budget("sk-user-abc", "pro")
    assert captured["url"] == "https://litellm.example.com/key/update"
    assert captured["json"]["key"] == "sk-user-abc"
    assert captured["json"]["max_budget"] == 15.0
    assert captured["json"]["models"] == [
        "parakeet-groq",
        "parakeet-claude",
        "parakeet-gpt",
        "parakeet-gemini",
    ]


def test_update_key_budget_raises_on_error_status(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _FakeResponse(500, {}))
    with pytest.raises(RuntimeError, match="key/update failed"):
        litellm_service.update_key_budget("sk-user-abc", "free")


def test_mint_key_defaults_unknown_tier_to_free_budget(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    captured = {}
    monkeypatch.setattr(
        httpx, "post",
        lambda url, headers, json, timeout: captured.update(json=json) or _FakeResponse(200, {"key": "sk-x"}),
    )
    litellm_service.mint_key("user-1", "unknown-tier")
    assert captured["json"]["max_budget"] == 1.0


def test_mint_key_raises_on_error_status(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _FakeResponse(500, {}))
    with pytest.raises(RuntimeError, match="key/generate failed"):
        litellm_service.mint_key("user-1", "free")


def test_get_spend_returns_zeros_on_error(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: _FakeResponse(404, {}))
    assert litellm_service.get_spend("sk-user-abc") == (0.0, 0.0)


def test_get_spend_parses_nested_info(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    monkeypatch.setattr(
        httpx, "get",
        lambda *a, **kw: _FakeResponse(200, {"info": {"spend": 0.42, "max_budget": 1.0}}),
    )
    assert litellm_service.get_spend("sk-user-abc") == (0.42, 1.0)


def test_get_spend_parses_flat_payload(monkeypatch):
    monkeypatch.setenv("LITELLM_URL", "https://litellm.example.com")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "sk-master-test")
    monkeypatch.setattr(
        httpx, "get",
        lambda *a, **kw: _FakeResponse(200, {"spend": 2.0, "max_budget": 15.0}),
    )
    assert litellm_service.get_spend("sk-user-abc") == (2.0, 15.0)
