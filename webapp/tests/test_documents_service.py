import httpx
import pytest

from webapp.services import documents


def test_chunk_empty_text_returns_no_chunks():
    assert documents.chunk("") == []


def test_chunk_short_text_returns_single_chunk():
    assert documents.chunk("hello world", size=500, overlap=60) == ["hello world"]


def test_chunk_splits_by_word_count_with_overlap():
    words = [f"w{i}" for i in range(12)]
    text = " ".join(words)
    chunks = documents.chunk(text, size=5, overlap=2)
    assert chunks[0] == "w0 w1 w2 w3 w4"
    assert chunks[1] == "w3 w4 w5 w6 w7"
    assert chunks[-1].endswith("w11")


def test_extract_text_plain_txt_decodes_utf8():
    data = "hello résumé".encode("utf-8")
    assert documents.extract_text(data, "notes.txt") == "hello résumé"


def test_extract_text_unknown_extension_falls_back_to_utf8():
    data = "raw content".encode("utf-8")
    assert documents.extract_text(data, "notes.weird") == "raw content"


def test_embed_returns_empty_list_for_no_texts():
    assert documents.embed([]) == []


def test_embed_calls_edge_function_with_secret(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_FUNCTIONS_URL", raising=False)
    monkeypatch.setenv("EMBED_SECRET", "shh")
    captured = {}

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {"embeddings": [[0.1, 0.2]]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)
    vectors = documents.embed(["hello"])
    assert vectors == [[0.1, 0.2]]
    assert captured["url"] == "https://example.supabase.co/functions/v1/rag"
    assert captured["headers"]["x-embed-secret"] == "shh"
    assert captured["json"] == {"action": "embed", "texts": ["hello"]}


def test_embed_prefers_explicit_functions_url(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_FUNCTIONS_URL", "https://example.supabase.co/functions/v1")
    captured = {}

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {"embeddings": []}

    monkeypatch.setattr(httpx, "post", lambda url, **kw: captured.update(url=url) or _FakeResponse())
    documents.embed(["x"])
    assert captured["url"] == "https://example.supabase.co/functions/v1/rag"


def test_embed_raises_on_error_status(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")

    class _FakeResponse:
        status_code = 500
        text = "boom"

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _FakeResponse())
    with pytest.raises(RuntimeError, match="embed failed"):
        documents.embed(["hello"])
