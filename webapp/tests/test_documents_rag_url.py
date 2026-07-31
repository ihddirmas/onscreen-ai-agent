"""Tests for rag_url helper."""
import os

from webapp.services import documents


def test_rag_url_from_functions_url(monkeypatch):
    monkeypatch.setenv("SUPABASE_FUNCTIONS_URL", "https://proj.supabase.co/functions/v1")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert documents.rag_url() == "https://proj.supabase.co/functions/v1/rag"


def test_rag_url_from_supabase_url(monkeypatch):
    monkeypatch.delenv("SUPABASE_FUNCTIONS_URL", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    assert documents.rag_url() == "https://proj.supabase.co/functions/v1/rag"


def test_rag_url_empty_without_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_FUNCTIONS_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert documents.rag_url() == ""
