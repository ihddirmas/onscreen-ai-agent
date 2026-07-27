import pytest

from webapp.services import supabase as supabase_service


def test_anon_client_raises_without_url(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key")
    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        supabase_service.anon_client()


def test_anon_client_raises_without_anon_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SUPABASE_ANON_KEY"):
        supabase_service.anon_client()


def test_anon_client_builds_with_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key")
    captured = {}

    def fake_create_client(url, key):
        captured["url"] = url
        captured["key"] = key
        return "fake-client"

    monkeypatch.setattr(supabase_service, "create_client", fake_create_client)
    client = supabase_service.anon_client()
    assert client == "fake-client"
    assert captured == {"url": "https://example.supabase.co", "key": "anon-key"}


def test_admin_client_raises_without_service_role_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SUPABASE_SERVICE_ROLE_KEY"):
        supabase_service.admin_client()


def test_admin_client_builds_with_service_role_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    captured = {}

    def fake_create_client(url, key):
        captured["url"] = url
        captured["key"] = key
        return "fake-admin-client"

    monkeypatch.setattr(supabase_service, "create_client", fake_create_client)
    client = supabase_service.admin_client()
    assert client == "fake-admin-client"
    assert captured == {"url": "https://example.supabase.co", "key": "service-role-key"}
