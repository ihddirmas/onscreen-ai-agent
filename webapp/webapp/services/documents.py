"""Reference-document pipeline: extract text -> chunk -> embed. Chunking and
extraction run locally; embedding stays delegated to the existing Supabase
Edge Function (gte-small, 384-dim) so no embedding model ships with this
app. Mirrors website/lib/rag.ts and website/lib/extract.ts."""
from __future__ import annotations

import os
from io import BytesIO

import httpx

EMBED_DIM = 384


def chunk(text: str, size: int = 500, overlap: int = 60) -> list[str]:
    """Split text into ~size-word chunks with a small overlap for context."""
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    i = 0
    while True:
        piece = words[i : i + size]
        chunks.append(" ".join(piece))
        if i + size >= len(words):
            break
        i += size - overlap
    return chunks


def extract_text(data: bytes, filename: str) -> str:
    """Extract plain text from an uploaded file's bytes by extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if lower.endswith(".docx"):
        import docx

        document = docx.Document(BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)
    return data.decode("utf-8", errors="replace")


def _edge_url() -> str:
    explicit = os.environ.get("SUPABASE_FUNCTIONS_URL")
    if explicit:
        return f"{explicit.rstrip('/')}/rag"
    base = os.environ.get("SUPABASE_URL")
    if not base:
        raise RuntimeError("SUPABASE_URL or SUPABASE_FUNCTIONS_URL is not set")
    return f"{base.rstrip('/')}/functions/v1/rag"


def embed(texts: list[str]) -> list[list[float]]:
    """Embed strings via the Supabase Edge Function (server-to-server, shared secret)."""
    if not texts:
        return []
    secret = os.environ.get("EMBED_SECRET", "")
    response = httpx.post(
        _edge_url(),
        headers={"Content-Type": "application/json", "x-embed-secret": secret},
        json={"action": "embed", "texts": texts},
        timeout=30.0,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"embed failed: {response.status_code} {response.text}")
    return response.json()["embeddings"]
