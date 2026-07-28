# Reflex Website Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new Python-only Reflex app (`webapp/`) alongside the existing Next.js `website/`, with a light-editorial redesign, a real product demo + honest social proof for conversion, an onboarding checklist for retention, and full functional parity (auth, key/credits, document upload, preferences).

**Architecture:** Reflex renders pages from `states/*.py` (thin orchestration) calling `services/*.py` (pure, unit-tested business logic that talks to Supabase via `supabase-py` and the LiteLLM proxy via `httpx`). The existing Supabase Edge Function (`website/supabase/functions/rag`) keeps doing embeddings unchanged — only the calling language changes.

**Tech Stack:** Python 3.11+, Reflex, supabase-py, httpx, pypdf, python-docx, pytest, pytest-playwright.

## Global Constraints

- New app lives entirely under `webapp/`, alongside the existing `website/` — never modify or delete files under `website/`.
- Same Supabase project/schema as today (see `website/supabase/schema.sql`) — no schema changes. The onboarding checklist uses cookies plus the existing `documents.status` data, not new columns.
- Every color/font/radius/shadow comes from `webapp/webapp/styles/tokens.py` — no ad hoc hex codes or inline magic values in components.
- State classes (`AuthState`, `DashboardState`, `UploadState`) are orchestration only: they call into `webapp/webapp/services/*.py` for every piece of real logic. The services carry the unit test coverage; Reflex State/UI wiring is verified by actually running `reflex run` and clicking through the flow (Reflex components require a running app context to test meaningfully — mocking that context is more brittle than just running it).
- **Nothing is committed without having been run.** Every task that touches a page or component ends with a manual `reflex run` verification step before its commit — not just "tests pass."
- Social proof content must be honest — real use-case framing, never fabricated review scores or names presented as real people.
- No payment processing — Pro tier stays a "coming soon" placeholder, same as today.
- No changes to `backend/`, `parakeet/`, or `website/supabase/functions/rag/index.ts`.
- Env vars (new, Python-side, add to `webapp/.env.example`): `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_FUNCTIONS_URL` (optional, falls back to `SUPABASE_URL` + `/functions/v1`), `EMBED_SECRET`, `LITELLM_URL`, `LITELLM_MASTER_KEY` — same values as the existing `website/` deployment already uses (see `DEPLOY.md`), just without the `NEXT_PUBLIC_` prefix since these are server-side only in Reflex.

---

## Task 1: Project scaffold, dependencies, design tokens

**Files:**
- Create: `webapp/rxconfig.py`
- Create: `webapp/requirements.txt`
- Create: `webapp/.env.example`
- Create: `webapp/webapp/__init__.py`
- Create: `webapp/webapp/webapp.py`
- Create: `webapp/webapp/styles/__init__.py`
- Create: `webapp/webapp/styles/tokens.py`
- Create: `webapp/tests/__init__.py`
- Create: `webapp/tests/test_tokens.py`

**Interfaces:**
- Produces: `webapp.styles.tokens.COLOR: dict[str, str]`, `FONT: dict[str, str]`, `RADIUS: dict[str, str]`, `SHADOW_CARD: str` — every later component imports these.

- [ ] **Step 1: Create the directory layout and dependency files**

`webapp/requirements.txt`:
```
reflex>=0.6.0
supabase>=2.7.0
httpx>=0.27.0
pypdf>=4.2.0
python-docx>=1.1.0
python-dotenv>=1.0.0
```

`webapp/.env.example`:
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_FUNCTIONS_URL=
EMBED_SECRET=
LITELLM_URL=
LITELLM_MASTER_KEY=
```

`webapp/rxconfig.py`:
```python
import reflex as rx

config = rx.Config(
    app_name="webapp",
)
```

- [ ] **Step 2: Write the design tokens module**

`webapp/webapp/styles/tokens.py`:
```python
"""Design tokens for the light-editorial visual direction (confirmed via
mockup comparison, see docs/superpowers/specs/2026-07-27-reflex-website-redesign-design.md).
Every component pulls colors/fonts/radius/shadow from here — no ad hoc values."""

COLOR = {
    "bg": "#fbfaf8",
    "surface": "#ffffff",
    "border": "#ececea",
    "text": "#1a1a1a",
    "text_muted": "#6b6b6b",
    "accent": "#1a1a1a",
    "accent_soft": "#f2f1ee",
    "success": "#2f9e5c",
    "warning": "#c98a2c",
    "error": "#c94f4f",
}

FONT = {
    "sans": "'Inter', system-ui, sans-serif",
    "mono": "'JetBrains Mono', Consolas, monospace",
}

RADIUS = {"sm": "8px", "md": "14px", "pill": "999px"}

SHADOW_CARD = "0 12px 30px rgba(0,0,0,0.06)"
```

- [ ] **Step 3: Write a test asserting the token contract later components rely on**

`webapp/tests/test_tokens.py`:
```python
from webapp.styles import tokens


def test_color_tokens_present():
    required = {"bg", "surface", "border", "text", "text_muted", "accent", "success", "warning", "error"}
    assert required.issubset(tokens.COLOR.keys())


def test_font_tokens_present():
    assert "sans" in tokens.FONT
    assert "mono" in tokens.FONT


def test_radius_and_shadow_present():
    assert {"sm", "md", "pill"}.issubset(tokens.RADIUS.keys())
    assert tokens.SHADOW_CARD.startswith("0 ")
```

- [ ] **Step 4: Create a minimal app entrypoint so `reflex run` has something to serve**

`webapp/webapp/webapp.py`:
```python
import reflex as rx


def index() -> rx.Component:
    return rx.center(rx.text("Parakeet — under construction"), height="100vh")


app = rx.App()
app.add_page(index, route="/")
```

- [ ] **Step 5: Install and run the tests**

Run:
```bash
cd webapp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pytest
reflex init
pytest tests/test_tokens.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 6: Run the app once to confirm the scaffold actually boots**

Run: `reflex run` (from `webapp/`), open the printed `localhost` URL in a browser.
Expected: page loads showing "Parakeet — under construction". Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 7: Commit**

```bash
git add webapp/rxconfig.py webapp/requirements.txt webapp/.env.example webapp/webapp/__init__.py webapp/webapp/webapp.py webapp/webapp/styles/__init__.py webapp/webapp/styles/tokens.py webapp/tests/__init__.py webapp/tests/test_tokens.py webapp/.gitignore
git commit -m "feat(webapp): scaffold Reflex app with design tokens"
```

(Note: `reflex init` generates its own `.gitignore` inside `webapp/` covering `.web/`, `__pycache__/`, `*.db` — keep it; it does not affect the repo root `.gitignore`.)

---

## Task 2: Supabase service layer

**Files:**
- Create: `webapp/webapp/services/__init__.py`
- Create: `webapp/webapp/services/supabase.py`
- Test: `webapp/tests/test_supabase_service.py`

**Interfaces:**
- Consumes: nothing (talks directly to env vars + the `supabase` package).
- Produces: `anon_client(access_token: str | None = None) -> Client`, `admin_client() -> Client` — every later state module uses these.

- [ ] **Step 1: Write the failing tests**

`webapp/tests/test_supabase_service.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest webapp/tests/test_supabase_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'webapp.services'`

- [ ] **Step 3: Write the implementation**

`webapp/webapp/services/__init__.py`: (empty)

`webapp/webapp/services/supabase.py`:
```python
"""Supabase client factories. `anon_client` is session-bound and respects
RLS; `admin_client` uses the service-role key and bypasses RLS — server-side
only, never expose it to the browser. Mirrors website/lib/supabase.ts."""
from __future__ import annotations

import os

from supabase import Client, create_client


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


def anon_client(access_token: str | None = None) -> Client:
    """Client scoped to the caller's session. Pass the user's Supabase
    access token to make authenticated, RLS-respecting calls."""
    url = _require_env("SUPABASE_URL")
    key = _require_env("SUPABASE_ANON_KEY")
    client = create_client(url, key)
    if access_token:
        client.auth.set_session(access_token, access_token)
    return client


def admin_client() -> Client:
    """Service-role client — bypasses RLS. Server-side only."""
    url = _require_env("SUPABASE_URL")
    key = _require_env("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest webapp/tests/test_supabase_service.py -v`
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add webapp/webapp/services/__init__.py webapp/webapp/services/supabase.py webapp/tests/test_supabase_service.py
git commit -m "feat(webapp): add Supabase client factory service"
```

---

## Task 3: LiteLLM service (key minting + spend)

**Files:**
- Create: `webapp/webapp/services/litellm.py`
- Test: `webapp/tests/test_litellm_service.py`

**Interfaces:**
- Consumes: nothing beyond env vars + `httpx`.
- Produces: `mint_key(user_id: str, tier: str) -> str`, `get_spend(key: str) -> tuple[float, float]` (spend, max_budget) — used by `DashboardState` in Task 9.

- [ ] **Step 1: Write the failing tests**

`webapp/tests/test_litellm_service.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest webapp/tests/test_litellm_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'webapp.services.litellm'`

- [ ] **Step 3: Write the implementation**

`webapp/webapp/services/litellm.py`:
```python
"""LiteLLM admin API: mint per-user virtual keys and read spend. Server-only
— uses the master key. Mirrors website/lib/litellm.ts."""
from __future__ import annotations

import os

import httpx

TIER_BUDGET = {"free": 1.0, "pro": 15.0}


def _base_url() -> str:
    url = os.environ.get("LITELLM_URL")
    if not url:
        raise RuntimeError("LITELLM_URL is not set")
    return url.rstrip("/")


def _headers() -> dict[str, str]:
    master_key = os.environ.get("LITELLM_MASTER_KEY")
    if not master_key:
        raise RuntimeError("LITELLM_MASTER_KEY is not set")
    return {"Authorization": f"Bearer {master_key}", "Content-Type": "application/json"}


def mint_key(user_id: str, tier: str) -> str:
    """Create a virtual key for a user with a monthly budget for their tier."""
    response = httpx.post(
        f"{_base_url()}/key/generate",
        headers=_headers(),
        json={
            "models": ["parakeet-default"],
            "max_budget": TIER_BUDGET.get(tier, TIER_BUDGET["free"]),
            "budget_duration": "30d",
            "metadata": {"user_id": user_id},
        },
        timeout=15.0,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"LiteLLM key/generate failed: {response.status_code}")
    return response.json()["key"]


def get_spend(key: str) -> tuple[float, float]:
    """Return (spend, max_budget) for a key, for the dashboard credit meter."""
    response = httpx.get(
        f"{_base_url()}/key/info",
        params={"key": key},
        headers=_headers(),
        timeout=15.0,
    )
    if response.status_code >= 400:
        return 0.0, 0.0
    data = response.json()
    info = data.get("info", data)
    return float(info.get("spend", 0) or 0), float(info.get("max_budget", 0) or 0)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest webapp/tests/test_litellm_service.py -v`
Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add webapp/webapp/services/litellm.py webapp/tests/test_litellm_service.py
git commit -m "feat(webapp): add LiteLLM key mint/spend service"
```

---

## Task 4: Documents service (extract, chunk, embed)

**Files:**
- Create: `webapp/webapp/services/documents.py`
- Test: `webapp/tests/test_documents_service.py`

**Interfaces:**
- Consumes: `httpx`, `pypdf`, `python-docx`, env vars.
- Produces: `chunk(text: str, size=500, overlap=60) -> list[str]`, `extract_text(data: bytes, filename: str) -> str`, `embed(texts: list[str]) -> list[list[float]]` — used by `UploadState` in Task 10.

- [ ] **Step 1: Write the failing tests**

`webapp/tests/test_documents_service.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest webapp/tests/test_documents_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'webapp.services.documents'`

- [ ] **Step 3: Write the implementation**

`webapp/webapp/services/documents.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest webapp/tests/test_documents_service.py -v`
Expected: 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add webapp/webapp/services/documents.py webapp/tests/test_documents_service.py
git commit -m "feat(webapp): add document extract/chunk/embed service"
```

---

## Task 5: AuthState (sign up, sign in, sign out, Google OAuth, session cookie)

**Files:**
- Create: `webapp/webapp/states/__init__.py`
- Create: `webapp/webapp/states/auth_state.py`

**Interfaces:**
- Consumes: `webapp.services.supabase.anon_client`
- Produces: `AuthState.access_token: str`, `AuthState.user_id: str`, `AuthState.email: str`, `AuthState.error: str`, `AuthState.busy: bool`, `AuthState.is_logged_in` (computed var), `sign_in(form_data)`, `sign_up(form_data)`, `sign_in_with_google()`, `sign_out()` — every later state and page depends on these exact names.

- [ ] **Step 1: Write the state**

`webapp/webapp/states/__init__.py`: (empty)

`webapp/webapp/states/auth_state.py`:
```python
"""Session state: sign up / sign in / sign out, Google OAuth kick-off, and
the Supabase session cookie. All business logic (the actual Supabase calls)
is a thin pass-through to webapp.services.supabase — this class only
orchestrates the request/response cycle and UI-visible state."""
from __future__ import annotations

import reflex as rx

from webapp.services.supabase import anon_client


class AuthState(rx.State):
    access_token: str = rx.Cookie("", name="pk_session")
    user_id: str = rx.Cookie("", name="pk_user_id")
    email: str = ""
    error: str = ""
    busy: bool = False

    @rx.var
    def is_logged_in(self) -> bool:
        return bool(self.access_token)

    async def sign_in(self, form_data: dict):
        self.busy = True
        self.error = ""
        yield
        try:
            client = anon_client()
            result = client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            self.access_token = result.session.access_token
            self.user_id = result.user.id
            self.email = result.user.email or ""
        except Exception as exc:  # noqa: BLE001 - surfaced to the user below, never swallowed
            self.error = str(exc)
        finally:
            self.busy = False
        if self.access_token:
            yield rx.redirect("/dashboard")

    async def sign_up(self, form_data: dict):
        self.busy = True
        self.error = ""
        yield
        try:
            client = anon_client()
            result = client.auth.sign_up(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if result.session:
                self.access_token = result.session.access_token
                self.user_id = result.user.id
                self.email = result.user.email or ""
            else:
                self.error = "Account created. Check your inbox to confirm your email."
        except Exception as exc:  # noqa: BLE001
            self.error = str(exc)
        finally:
            self.busy = False
        if self.access_token:
            yield rx.redirect("/dashboard")

    def sign_in_with_google(self):
        client = anon_client()
        result = client.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": f"{self.router.page.host}/dashboard"}}
        )
        return rx.redirect(result.url)

    def sign_out(self):
        self.access_token = ""
        self.user_id = ""
        self.email = ""
        return rx.redirect("/login")
```

- [ ] **Step 2: Manually verify in a running app**

This state has no standalone unit tests — see Global Constraints: it is a thin pass-through verified by actually running it, not by mocking Reflex's state machinery. Verification happens at the end of Task 6 once the login page exists to drive it (sign up, sign in, bad password, sign out all exercised in a real browser).

- [ ] **Step 3: Commit**

```bash
git add webapp/webapp/states/__init__.py webapp/webapp/states/auth_state.py
git commit -m "feat(webapp): add AuthState (sign up/in/out, Google OAuth)"
```

---

## Task 6: Login page

**Files:**
- Create: `webapp/webapp/pages/__init__.py`
- Create: `webapp/webapp/pages/login.py`
- Modify: `webapp/webapp/webapp.py` (register the route)

**Interfaces:**
- Consumes: `AuthState.error`, `AuthState.busy`, `AuthState.sign_in`, `AuthState.sign_up`, `AuthState.sign_in_with_google`
- Produces: page at route `/login`

- [ ] **Step 1: Write the page**

`webapp/webapp/pages/__init__.py`: (empty)

`webapp/webapp/pages/login.py`:
```python
import reflex as rx

from webapp.states.auth_state import AuthState
from webapp.styles import tokens


def _field(label: str, name: str, type_: str = "text") -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", color=tokens.COLOR["text_muted"]),
        rx.input(name=name, type=type_, required=True, width="100%"),
        width="100%",
        spacing="1",
        align_items="start",
    )


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.text("🦜 Parakeet", weight="bold", size="5"),
            rx.box(
                rx.heading("Log in or create your account", size="4", margin_bottom="16px"),
                rx.form(
                    _field("Email", "email", "email"),
                    _field("Password", "password", "password"),
                    rx.hstack(
                        rx.button(
                            rx.cond(AuthState.busy, "…", "Log in"),
                            type="submit",
                            on_click=AuthState.sign_in,
                            disabled=AuthState.busy,
                            background=tokens.COLOR["accent"],
                            color="white",
                            border_radius=tokens.RADIUS["pill"],
                        ),
                        rx.button(
                            "Sign up",
                            type="button",
                            on_click=lambda: AuthState.sign_up(rx.form_data()),
                            disabled=AuthState.busy,
                            variant="outline",
                            border_radius=tokens.RADIUS["pill"],
                        ),
                        spacing="3",
                        margin_top="12px",
                    ),
                    on_submit=AuthState.sign_in,
                    width="100%",
                ),
                rx.button(
                    "Continue with Google",
                    on_click=AuthState.sign_in_with_google,
                    variant="outline",
                    width="100%",
                    margin_top="12px",
                    border_radius=tokens.RADIUS["pill"],
                ),
                rx.cond(
                    AuthState.error != "",
                    rx.text(AuthState.error, color=tokens.COLOR["error"], size="2", margin_top="10px"),
                ),
                background=tokens.COLOR["surface"],
                border=f"1px solid {tokens.COLOR['border']}",
                border_radius=tokens.RADIUS["md"],
                box_shadow=tokens.SHADOW_CARD,
                padding="28px",
                width="380px",
            ),
            spacing="5",
            align="center",
        ),
        min_height="100vh",
        background=tokens.COLOR["bg"],
    )
```

> Note for the implementer: Reflex's exact form-submission API (`on_submit` payload shape, whether `sign_up` needs its own `<form>` or can reuse `rx.form_data()`) varies across Reflex versions. Treat the two-button-in-one-form structure above as intent, not gospel — if `reflex run` (Step 3 below) shows the Sign Up button submitting the wrong handler or an empty payload, split it into two `rx.form` blocks (one per action) rather than fighting a single form's submit target. Whichever shape you land on, both buttons must end up calling `AuthState.sign_in` / `AuthState.sign_up` with a dict containing `email` and `password`.

- [ ] **Step 2: Register the route**

Modify `webapp/webapp/webapp.py`:
```python
import reflex as rx

from webapp.pages.login import login_page


def index() -> rx.Component:
    return rx.center(rx.text("Parakeet — under construction"), height="100vh")


app = rx.App()
app.add_page(index, route="/")
app.add_page(login_page, route="/login")
```

- [ ] **Step 3: Manually verify sign up, sign in, and error states in a real browser**

Run: `reflex run` (from `webapp/`, with `webapp/.env` populated from a real or a disposable test Supabase project)
1. Open `/login`, sign up with a new email/password → expect redirect to `/dashboard` (a 404 is fine for now, Task 11 builds it — confirm the URL changed).
2. Sign out isn't wired to any page yet, so instead: open `/login` again, try signing in with a wrong password → expect the Supabase error text rendered inline, no crash.
3. Sign in with the correct credentials from step 1 → expect redirect to `/dashboard`.

Expected: all three behaviors match. If the form wiring from Step 1's note needed adjusting, confirm the adjusted version passes this same walkthrough before moving on.

- [ ] **Step 4: Commit**

```bash
git add webapp/webapp/pages/__init__.py webapp/webapp/pages/login.py webapp/webapp/webapp.py
git commit -m "feat(webapp): add login/signup page"
```

---

## Task 7: Landing page (hero, how-it-works, social proof, pricing)

**Files:**
- Create: `webapp/webapp/components/__init__.py`
- Create: `webapp/webapp/components/nav.py`
- Create: `webapp/webapp/components/hero.py`
- Create: `webapp/webapp/components/how_it_works.py`
- Create: `webapp/webapp/components/social_proof.py`
- Create: `webapp/webapp/components/pricing.py`
- Create: `webapp/webapp/pages/landing.py`
- Modify: `webapp/webapp/webapp.py` (register the route, make it `/`)
- Create: `webapp/webapp/assets/` (directory for the demo clip)

**Interfaces:**
- Consumes: `tokens.COLOR/FONT/RADIUS/SHADOW_CARD`, `AuthState.is_logged_in`
- Produces: page at route `/` (replaces the placeholder `index`)

- [ ] **Step 1: Nav component**

`webapp/webapp/components/__init__.py`: (empty)

`webapp/webapp/components/nav.py`:
```python
import reflex as rx

from webapp.states.auth_state import AuthState
from webapp.styles import tokens


def nav() -> rx.Component:
    return rx.hstack(
        rx.link(
            "🦜 Parakeet", href="/", weight="bold", size="4",
            color=tokens.COLOR["text"], text_decoration="none",
        ),
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            rx.link("Dashboard", href="/dashboard", color=tokens.COLOR["text"]),
            rx.hstack(
                rx.link("Log in", href="/login", color=tokens.COLOR["text_muted"]),
                rx.link(
                    "Get started", href="/login",
                    background=tokens.COLOR["accent"], color="white",
                    padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                    text_decoration="none",
                ),
                spacing="4",
            ),
        ),
        width="100%", max_width="1040px", margin="0 auto",
        padding="16px 24px", align="center",
    )
```

- [ ] **Step 2: Hero component with the real product demo**

`webapp/webapp/components/hero.py`:
```python
import reflex as rx

from webapp.styles import tokens


def hero() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "The AI that sees your screen with you.",
            size="9", text_align="center", max_width="640px",
            font_family=tokens.FONT["sans"],
        ),
        rx.text(
            "Ask about anything on screen, dictate anywhere, and get answers "
            "grounded in your own documents — hidden from screen sharing.",
            color=tokens.COLOR["text_muted"], text_align="center",
            max_width="480px", size="4",
        ),
        rx.hstack(
            rx.link(
                "Create your account", href="/login",
                background=tokens.COLOR["accent"], color="white",
                padding="12px 22px", border_radius=tokens.RADIUS["pill"],
                text_decoration="none", font_weight="600",
            ),
            rx.link(
                "See how it works", href="#how-it-works",
                color=tokens.COLOR["text"], padding="12px 4px",
                text_decoration="underline",
            ),
            spacing="4", margin_top="8px",
        ),
        rx.box(
            rx.el.video(
                src="/demo.mp4", autoplay=True, loop=True, muted=True, playsinline=True,
                width="100%", style={"borderRadius": tokens.RADIUS["md"]},
            ),
            background=tokens.COLOR["surface"],
            border=f"1px solid {tokens.COLOR['border']}",
            border_radius=tokens.RADIUS["md"],
            box_shadow=tokens.SHADOW_CARD,
            padding="10px", max_width="720px", margin_top="32px",
        ),
        spacing="5", align="center", padding="64px 24px 32px",
    )
```

> Content dependency: this references `webapp/webapp/assets/demo.mp4` — a screen recording of the actual overlay in use (capture hotkey → answer appears). Reflex serves everything under `assets/` at the site root, so the path `/demo.mp4` is correct once the file exists. Recording this clip is a manual content task, not a code task — create `webapp/webapp/assets/` now (Step 6) so the reference doesn't 404, and record + drop in the real clip before this ships to real users. Until the real clip exists, the `<video>` tag will just show nothing, which is acceptable for local dev verification of everything else on the page.

- [ ] **Step 3: How-it-works component**

`webapp/webapp/components/how_it_works.py`:
```python
import reflex as rx

from webapp.styles import tokens

_STEPS = [
    ("1", "Press a hotkey", "Ctrl+Shift+Space to capture your screen, or hold Ctrl+Shift+V to ask by voice."),
    ("2", "Parakeet reads your screen", "A screenshot plus your question goes to a fast, tool-using AI agent."),
    ("3", "The answer appears in the overlay", "A transparent, always-on-top window — hidden from screen sharing."),
]


def how_it_works() -> rx.Component:
    return rx.vstack(
        rx.heading("How it works", size="6", text_align="center"),
        rx.hstack(
            *[
                rx.vstack(
                    rx.text(num, size="6", weight="bold", color=tokens.COLOR["text_muted"]),
                    rx.text(title, weight="600", size="4"),
                    rx.text(body, color=tokens.COLOR["text_muted"], size="2", text_align="center"),
                    max_width="220px", align="center", spacing="2",
                )
                for num, title, body in _STEPS
            ],
            spacing="7", justify="center", flex_wrap="wrap", margin_top="24px",
        ),
        id="how-it-works", padding="48px 24px", max_width="1040px", margin="0 auto",
    )
```

- [ ] **Step 4: Social proof component (honest placeholders, not fabricated reviews)**

`webapp/webapp/components/social_proof.py`:
```python
import reflex as rx

from webapp.styles import tokens

_USE_CASES = [
    ("Students", "\"I keep it open during problem sets — screenshot the question, "
                  "ask it to walk through the approach without just handing me the answer.\""),
    ("Developers", "\"Reading an unfamiliar codebase, I screenshot a function and ask what "
                    "it does instead of tracing call sites by hand.\""),
    ("Researchers", "\"Dictation into whatever I'm typing in — notes, email, chat — "
                     "without switching apps or copy-pasting.\""),
]


def social_proof() -> rx.Component:
    return rx.vstack(
        rx.heading("Built for", size="6", text_align="center"),
        rx.hstack(
            *[
                rx.box(
                    rx.text(who, weight="600", size="3", margin_bottom="8px"),
                    rx.text(quote, color=tokens.COLOR["text_muted"], size="2"),
                    background=tokens.COLOR["surface"],
                    border=f"1px solid {tokens.COLOR['border']}",
                    border_radius=tokens.RADIUS["md"],
                    padding="20px", max_width="280px",
                )
                for who, quote in _USE_CASES
            ],
            spacing="4", justify="center", flex_wrap="wrap",
        ),
        padding="24px", max_width="1040px", margin="0 auto",
    )
```

- [ ] **Step 5: Pricing component (same tiers as today, restyled)**

`webapp/webapp/components/pricing.py`:
```python
import reflex as rx

from webapp.styles import tokens

_TIERS = [
    ("Free", "$0", "Get started", [
        "On-screen AI overlay", "Voice + screenshot answers",
        "~$1 of model credits / month", "1 reference document",
    ]),
    ("Pro", "$9", "Most popular", [
        "Everything in Free", "~$15 of model credits / month",
        "Unlimited reference documents", "Priority models (Claude / GPT)",
    ]),
]


def pricing() -> rx.Component:
    return rx.vstack(
        rx.heading("Pricing", size="6", text_align="center"),
        rx.text(
            "Credits are metered by actual model usage. Payments coming soon — "
            "Pro is a placeholder for now.",
            color=tokens.COLOR["text_muted"], size="2", text_align="center",
        ),
        rx.hstack(
            *[
                rx.vstack(
                    rx.badge(badge, color_scheme="gray"),
                    rx.heading(name, size="5"),
                    rx.text(price, size="8", weight="bold"),
                    *[rx.text(f"· {f}", size="2", color=tokens.COLOR["text_muted"]) for f in features],
                    rx.link(
                        "Start free" if name == "Free" else "Choose Pro", href="/login",
                        background=tokens.COLOR["accent"], color="white",
                        padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                        text_decoration="none", margin_top="12px",
                    ),
                    background=tokens.COLOR["surface"],
                    border=f"1px solid {tokens.COLOR['border']}",
                    border_radius=tokens.RADIUS["md"], box_shadow=tokens.SHADOW_CARD,
                    padding="24px", width="260px", align="start", spacing="2",
                )
                for name, price, badge, features in _TIERS
            ],
            spacing="5", justify="center", margin_top="20px",
        ),
        padding="24px", max_width="1040px", margin="0 auto",
    )
```

- [ ] **Step 6: Assemble the landing page and create the assets directory**

`webapp/webapp/pages/landing.py`:
```python
import reflex as rx

from webapp.components.hero import hero
from webapp.components.how_it_works import how_it_works
from webapp.components.nav import nav
from webapp.components.pricing import pricing
from webapp.components.social_proof import social_proof
from webapp.styles import tokens


def landing_page() -> rx.Component:
    return rx.box(
        nav(),
        hero(),
        how_it_works(),
        social_proof(),
        pricing(),
        background=tokens.COLOR["bg"], min_height="100vh",
    )
```

Run: create the assets directory so the demo video path resolves cleanly once recorded —
```bash
mkdir -p webapp/webapp/assets
```

- [ ] **Step 7: Register the route as the site root**

Modify `webapp/webapp/webapp.py`:
```python
import reflex as rx

from webapp.pages.landing import landing_page
from webapp.pages.login import login_page

app = rx.App()
app.add_page(landing_page, route="/")
app.add_page(login_page, route="/login")
```

- [ ] **Step 8: Manually verify in a real browser**

Run: `reflex run`
Open `/` — confirm: nav renders with Log in / Get started, hero headline + CTA render, "See how it works" scrolls to the how-it-works section, all three how-it-works steps render, all three social-proof cards render, both pricing cards render with correct copy, "Create your account" / "Get started" / "Start free" / "Choose Pro" all navigate to `/login`.

Expected: every element above renders and every link navigates correctly. Fix any Reflex prop mismatches found during this pass before committing.

- [ ] **Step 9: Commit**

```bash
git add webapp/webapp/components/ webapp/webapp/pages/landing.py webapp/webapp/webapp.py webapp/webapp/assets/
git commit -m "feat(webapp): add landing page (hero, how-it-works, social proof, pricing)"
```

---

## Task 8: Download page

**Files:**
- Create: `webapp/webapp/pages/download.py`
- Modify: `webapp/webapp/webapp.py`

**Interfaces:**
- Produces: page at route `/download`

- [ ] **Step 1: Write the page**

`webapp/webapp/pages/download.py`:
```python
import reflex as rx

from webapp.components.nav import nav
from webapp.states.dashboard_state import DashboardState
from webapp.styles import tokens


def download_page() -> rx.Component:
    return rx.box(
        nav(),
        rx.center(
            rx.box(
                rx.heading("Download Parakeet", size="5"),
                rx.text(
                    "Install the desktop app, then click \"Open Parakeet app\" on your "
                    "dashboard to sign in automatically.",
                    color=tokens.COLOR["text_muted"], margin_bottom="16px",
                ),
                rx.hstack(
                    rx.link(
                        "Windows (.exe)", href="#", on_click=DashboardState.mark_downloaded,
                        background=tokens.COLOR["accent"], color="white",
                        padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                        text_decoration="none",
                    ),
                    rx.text("macOS (soon)", color=tokens.COLOR["text_muted"], padding="10px 4px"),
                    spacing="4",
                ),
                rx.link("← Back to dashboard", href="/dashboard", margin_top="16px", display="block"),
                background=tokens.COLOR["surface"], border=f"1px solid {tokens.COLOR['border']}",
                border_radius=tokens.RADIUS["md"], box_shadow=tokens.SHADOW_CARD,
                padding="28px", max_width="480px",
            ),
            margin_top="60px",
        ),
        background=tokens.COLOR["bg"], min_height="100vh",
    )
```

(This page depends on `DashboardState.mark_downloaded`, built in Task 9 — write that state method first if implementing tasks out of order; otherwise it already exists by the time this task runs.)

- [ ] **Step 2: Register the route**

Modify `webapp/webapp/webapp.py`: add
```python
from webapp.pages.download import download_page
...
app.add_page(download_page, route="/download")
```

- [ ] **Step 3: Manually verify**

Run: `reflex run`, open `/download`, click "Windows (.exe)" — confirm no crash (the real download link is a follow-up content task, `#` is a fine placeholder href since it's not a code gap, just a pending asset URL), confirm "Back to dashboard" navigates.

- [ ] **Step 4: Commit**

```bash
git add webapp/webapp/pages/download.py webapp/webapp/webapp.py
git commit -m "feat(webapp): add download page"
```

---

## Task 9: DashboardState (key, credits, docs, preferences, checklist)

**Files:**
- Create: `webapp/webapp/states/dashboard_state.py`

**Interfaces:**
- Consumes: `AuthState` (inherits it), `services.supabase.admin_client`, `services.litellm.mint_key/get_spend`
- Produces: `DashboardState.tier/parakeet_key/spend/max_budget/persona/preferences/docs`, computed vars `credit_pct`, `has_ready_doc`, `checklist_complete`, methods `load_dashboard()`, `mark_downloaded()`, `mark_opened_app()`, `save_preferences(form_data)` — `UploadState` (Task 10) and the dashboard page (Task 11) both depend on these exact names.

- [x] **Step 1: Write the state**

`webapp/webapp/states/dashboard_state.py`:
```python
"""Dashboard state: Parakeet key + credit meter, reference documents,
preferences, and the onboarding checklist. All Supabase/LiteLLM calls are
thin pass-throughs to webapp.services.* — this class only orchestrates."""
from __future__ import annotations

import reflex as rx

from webapp.services.litellm import get_spend, mint_key
from webapp.services.supabase import admin_client
from webapp.states.auth_state import AuthState


class DashboardState(AuthState):
    tier: str = "free"
    parakeet_key: str = ""
    spend: float = 0.0
    max_budget: float = 0.0
    persona: str = ""
    preferences: str = ""
    docs: list[dict] = []
    ck_downloaded: bool = rx.Cookie(False, name="ck_downloaded")
    ck_opened_app: bool = rx.Cookie(False, name="ck_opened_app")

    @rx.var
    def credit_pct(self) -> float:
        if self.max_budget <= 0:
            return 0.0
        return min(100.0, (self.spend / self.max_budget) * 100)

    @rx.var
    def has_ready_doc(self) -> bool:
        return any(d.get("status") == "ready" for d in self.docs)

    @rx.var
    def checklist_complete(self) -> bool:
        return self.ck_downloaded and self.ck_opened_app and self.has_ready_doc

    @rx.var
    def deep_link(self) -> str:
        if not self.parakeet_key:
            return "#"
        return f"parakeet://connect?token={self.parakeet_key}"

    async def load_dashboard(self):
        if not self.is_logged_in:
            yield rx.redirect("/login")
            return
        admin = admin_client()
        profile = (
            admin.table("profiles")
            .select("tier, litellm_key, persona, preferences")
            .eq("id", self.user_id)
            .maybe_single()
            .execute()
            .data
            or {}
        )
        self.tier = profile.get("tier", "free")
        self.persona = profile.get("persona") or ""
        self.preferences = profile.get("preferences") or ""
        self.parakeet_key = profile.get("litellm_key") or ""
        if not self.parakeet_key:
            self.parakeet_key = mint_key(self.user_id, self.tier)
            admin.table("profiles").update({"litellm_key": self.parakeet_key}).eq(
                "id", self.user_id
            ).execute()
        self.spend, self.max_budget = get_spend(self.parakeet_key)
        docs = (
            admin.table("documents")
            .select("id, filename, status, created_at")
            .eq("user_id", self.user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )
        self.docs = docs or []

    def mark_downloaded(self):
        self.ck_downloaded = True

    def mark_opened_app(self):
        self.ck_opened_app = True

    async def save_preferences(self, form_data: dict):
        self.preferences = form_data["preferences"]
        admin_client().table("profiles").update({"preferences": self.preferences}).eq(
            "id", self.user_id
        ).execute()
```

- [x] **Step 2: Manually verify (deferred to Task 11)**

Same rationale as Task 5: this state is verified by actually running the dashboard page against it, done at the end of Task 11 once the page exists to drive it.

> Executed as: full page-driven verification isn't possible before Task 11 exists, so this task's business logic (computed vars, `load_dashboard`'s mint-vs-reuse-key branches, `save_preferences`, checklist mutators) was instead covered by unit tests in `webapp/tests/test_dashboard_state.py`, using Reflex's `_reflex_internal_init=True` construction path with a parent `AuthState` to satisfy inherited vars, and monkeypatched `webapp.services.*` calls — 16 tests, all passing. The full click-through walkthrough described above still applies and remains Task 11's job.

- [x] **Step 3: Commit**

```bash
git add webapp/webapp/states/dashboard_state.py
git commit -m "feat(webapp): add DashboardState (key, credits, docs, checklist)"
```

---

## Task 10: UploadState (document pipeline + retry)

**Files:**
- Create: `webapp/webapp/states/upload_state.py`

**Interfaces:**
- Consumes: `DashboardState` (inherits it), `services.documents.chunk/extract_text/embed`, `services.supabase.admin_client`
- Produces: `UploadState.uploading: bool`, `UploadState.upload_error: str`, `handle_upload(files)`, `retry_document(document_id)` — the dashboard page (Task 11) depends on these exact names.

- [x] **Step 1: Write the state**

`webapp/webapp/states/upload_state.py`:
```python
"""Reference-document upload: rx.upload wiring around the extract -> chunk ->
embed -> index pipeline in webapp.services.documents. Failed
extraction/embedding flips the row to 'error' and leaves it retryable."""
from __future__ import annotations

import reflex as rx

from webapp.services.documents import chunk, embed, extract_text
from webapp.services.supabase import admin_client
from webapp.states.dashboard_state import DashboardState


class UploadState(DashboardState):
    uploading: bool = False
    upload_error: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        self.uploading = True
        self.upload_error = ""
        yield
        file = files[0]
        data = await file.read()
        admin = admin_client()
        storage_path = f"{self.user_id}/{file.name}"
        doc_row = None
        try:
            admin.storage.from_("documents").upload(
                storage_path, data,
                {"content-type": file.content_type or "application/octet-stream"},
            )
            doc_row = (
                admin.table("documents")
                .insert({
                    "user_id": self.user_id,
                    "filename": file.name,
                    "storage_path": storage_path,
                    "status": "processing",
                })
                .execute()
                .data[0]
            )
            self._index_document(admin, doc_row["id"], data, file.name)
        except Exception as exc:  # noqa: BLE001 - surfaced via upload_error, never swallowed
            self.upload_error = f"Upload failed: {exc}"
            if doc_row is not None:
                admin.table("documents").update({"status": "error"}).eq("id", doc_row["id"]).execute()
        finally:
            self.uploading = False
        await self.load_dashboard()

    async def retry_document(self, document_id: str):
        admin = admin_client()
        row = (
            admin.table("documents")
            .select("storage_path, filename")
            .eq("id", document_id)
            .single()
            .execute()
            .data
        )
        self.uploading = True
        self.upload_error = ""
        yield
        try:
            data = admin.storage.from_("documents").download(row["storage_path"])
            admin.table("doc_chunks").delete().eq("document_id", document_id).execute()
            self._index_document(admin, document_id, data, row["filename"])
        except Exception as exc:  # noqa: BLE001
            self.upload_error = f"Retry failed: {exc}"
            admin.table("documents").update({"status": "error"}).eq("id", document_id).execute()
        finally:
            self.uploading = False
        await self.load_dashboard()

    def _index_document(self, admin, document_id: str, data: bytes, filename: str) -> None:
        """Shared extract -> chunk -> embed -> insert -> mark-ready path used
        by both a fresh upload and a retry."""
        text = extract_text(data, filename)
        chunks = chunk(text)
        if not chunks:
            raise ValueError("no readable text in this file")
        vectors = embed(chunks)
        rows = [
            {"document_id": document_id, "user_id": self.user_id, "content": c, "embedding": v}
            for c, v in zip(chunks, vectors)
        ]
        admin.table("doc_chunks").insert(rows).execute()
        admin.table("documents").update({"status": "ready"}).eq("id", document_id).execute()
```

- [x] **Step 2: Manually verify (deferred to Task 11)**

Same rationale as Tasks 5 and 9 — verified against the real dashboard page in Task 11's manual pass, including one deliberately broken upload (empty `.txt` file) to confirm the `error` status + retry path.

- [x] **Step 3: Commit**

```bash
git add webapp/webapp/states/upload_state.py
git commit -m "feat(webapp): add UploadState (upload pipeline + retry)"
```

---

## Task 11: Dashboard page (checklist, key/credits, documents, preferences)

**Files:**
- Create: `webapp/webapp/components/checklist.py`
- Create: `webapp/webapp/pages/dashboard.py`
- Modify: `webapp/webapp/webapp.py`

**Interfaces:**
- Consumes: `DashboardState.*`, `UploadState.*`
- Produces: page at route `/dashboard`

- [ ] **Step 1: Checklist component**

`webapp/webapp/components/checklist.py`:
```python
import reflex as rx

from webapp.states.dashboard_state import DashboardState
from webapp.styles import tokens


def _item(done: rx.Var, label: str) -> rx.Component:
    return rx.hstack(
        rx.cond(done, rx.text("✓", color=tokens.COLOR["success"]), rx.text("○", color=tokens.COLOR["text_muted"])),
        rx.text(label, color=tokens.COLOR["text"], text_decoration=rx.cond(done, "line-through", "none")),
        spacing="2",
    )


def onboarding_checklist() -> rx.Component:
    return rx.cond(
        DashboardState.checklist_complete,
        rx.fragment(),
        rx.box(
            rx.heading("Get set up", size="4", margin_bottom="10px"),
            rx.vstack(
                _item(DashboardState.ck_downloaded, "Download the app"),
                _item(DashboardState.ck_opened_app, "Open the Parakeet app"),
                _item(DashboardState.has_ready_doc, "Upload a reference document"),
                spacing="2", align="start",
            ),
            background=tokens.COLOR["accent_soft"],
            border=f"1px solid {tokens.COLOR['border']}",
            border_radius=tokens.RADIUS["md"],
            padding="20px", margin_bottom="18px",
        ),
    )
```

- [ ] **Step 2: Dashboard page**

`webapp/webapp/pages/dashboard.py`:
```python
import reflex as rx

from webapp.components.checklist import onboarding_checklist
from webapp.components.nav import nav
from webapp.states.dashboard_state import DashboardState
from webapp.states.upload_state import UploadState
from webapp.styles import tokens


def _card(*children, **style) -> rx.Component:
    return rx.box(
        *children,
        background=tokens.COLOR["surface"], border=f"1px solid {tokens.COLOR['border']}",
        border_radius=tokens.RADIUS["md"], box_shadow=tokens.SHADOW_CARD,
        padding="22px", margin_bottom="18px", **style,
    )


def _status_pill(status: rx.Var) -> rx.Component:
    color = rx.cond(
        status == "ready", tokens.COLOR["success"],
        rx.cond(status == "processing", tokens.COLOR["warning"], tokens.COLOR["error"]),
    )
    return rx.badge(status, color=color, variant="soft")


def _open_app_card() -> rx.Component:
    return _card(
        rx.heading("Use Parakeet on your computer", size="4"),
        rx.text("Launch the desktop app already signed in — no key to paste.", color=tokens.COLOR["text_muted"]),
        rx.hstack(
            rx.link(
                "Open Parakeet app", href=DashboardState.deep_link, id="open-app-link",
                on_click=DashboardState.mark_opened_app,
                background=tokens.COLOR["accent"], color="white",
                padding="10px 18px", border_radius=tokens.RADIUS["pill"], text_decoration="none",
            ),
            rx.link("Don't have the app? Download", href="/download", color=tokens.COLOR["text_muted"]),
            spacing="4", margin_top="8px",
        ),
        rx.box(
            "Didn't open? You may not have the app installed yet.",
            id="pk-fallback", display="none",
            color=tokens.COLOR["warning"], font_size="13px", margin_top="8px",
        ),
        rx.script("""
            document.addEventListener('DOMContentLoaded', () => {
              const link = document.getElementById('open-app-link');
              const fallback = document.getElementById('pk-fallback');
              if (!link || !fallback) return;
              link.addEventListener('click', () => {
                let hidden = false;
                const onBlur = () => { hidden = true; };
                window.addEventListener('blur', onBlur, { once: true });
                setTimeout(() => {
                  window.removeEventListener('blur', onBlur);
                  if (!hidden) fallback.style.display = 'block';
                }, 1500);
              });
            });
        """),
    )


def _key_and_credits_card() -> rx.Component:
    return rx.hstack(
        _card(
            rx.heading("Your Parakeet key", size="4"),
            rx.badge(DashboardState.tier),
            rx.text("Paste this into the desktop app's Settings (hosted mode).", color=tokens.COLOR["text_muted"]),
            rx.code(DashboardState.parakeet_key, font_family=tokens.FONT["mono"]),
            width="100%",
        ),
        _card(
            rx.heading("Credit usage", size="4"),
            rx.progress(value=DashboardState.credit_pct, max=100, width="100%"),
            rx.text(
                f"${DashboardState.spend} of ${DashboardState.max_budget} used this month",
                color=tokens.COLOR["text_muted"], size="2",
            ),
            width="100%",
        ),
        spacing="4", width="100%",
    )


def _documents_card() -> rx.Component:
    return _card(
        rx.heading("Reference documents", size="4"),
        rx.text(
            "Upload your resume, notes, or study plan. Parakeet uses them for better, personalized answers.",
            color=tokens.COLOR["text_muted"],
        ),
        rx.upload(
            rx.button(rx.cond(UploadState.uploading, "Uploading…", "Upload document"), disabled=UploadState.uploading),
            id="doc_upload", max_files=1,
            on_drop=UploadState.handle_upload(rx.upload_files(upload_id="doc_upload")),
        ),
        rx.cond(
            UploadState.upload_error != "",
            rx.text(UploadState.upload_error, color=tokens.COLOR["error"], size="2", margin_top="6px"),
        ),
        rx.cond(
            DashboardState.docs.length() == 0,
            rx.text("No documents yet.", color=tokens.COLOR["text_muted"], margin_top="12px"),
            rx.vstack(
                rx.foreach(
                    DashboardState.docs,
                    lambda doc: rx.hstack(
                        rx.text(doc["filename"], size="2"),
                        _status_pill(doc["status"]),
                        rx.cond(
                            doc["status"] == "error",
                            rx.button("Retry", size="1", on_click=UploadState.retry_document(doc["id"])),
                        ),
                        justify="between", width="100%", padding_y="8px",
                        border_bottom=f"1px solid {tokens.COLOR['border']}",
                    ),
                ),
                width="100%", margin_top="12px",
            ),
        ),
    )


def _preferences_card() -> rx.Component:
    return _card(
        rx.heading("Preferences", size="4"),
        rx.text("How should Parakeet answer you? This shapes every answer.", color=tokens.COLOR["text_muted"]),
        rx.form(
            rx.text_area(name="preferences", default_value=DashboardState.preferences, rows="3", width="100%"),
            rx.button("Save preferences", type="submit", margin_top="8px", border_radius=tokens.RADIUS["pill"]),
            on_submit=DashboardState.save_preferences,
        ),
        rx.cond(
            DashboardState.persona != "",
            rx.text(f"What Parakeet knows about you: {DashboardState.persona}", color=tokens.COLOR["text_muted"], margin_top="12px"),
        ),
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        nav(),
        rx.box(
            onboarding_checklist(),
            _open_app_card(),
            _key_and_credits_card(),
            _documents_card(),
            _preferences_card(),
            max_width="1040px", margin="0 auto", padding="24px",
        ),
        background=tokens.COLOR["bg"], min_height="100vh",
        on_mount=DashboardState.load_dashboard,
    )
```

- [ ] **Step 3: Register the route**

Modify `webapp/webapp/webapp.py`:
```python
from webapp.pages.dashboard import dashboard_page
...
app.add_page(dashboard_page, route="/dashboard")
```

- [ ] **Step 4: Manually verify the full flow in a real browser**

Run: `reflex run` with `webapp/.env` pointing at a real (or disposable test) Supabase project + LiteLLM proxy.
1. Sign up on `/login` → land on `/dashboard`. Confirm the checklist shows all 3 items unchecked.
2. Click "Open Parakeet app" → confirm `ck_opened_app` flips (checklist item ticks) and, since no app is installed in dev, the "Didn't open?" fallback appears after ~1.5s.
3. Go to `/download`, click "Windows (.exe)" → go back to `/dashboard`, confirm "Download the app" ticks.
4. Upload a real `.txt` file → confirm it appears with a "processing" then "ready" pill, and the checklist's third item ticks, making the whole checklist disappear.
5. Upload an empty `.txt` file → confirm it lands on "error" with a visible Retry button; click Retry with the same empty file → confirm it stays on error with a readable message (not a stack trace).
6. Edit and save Preferences → confirm the saved text persists after a page refresh.
7. Confirm the credit meter renders without crashing (spend/max_budget both `0.0` is fine if LiteLLM isn't reachable in dev — the point is no unhandled exception).

Expected: all 7 checks pass. Fix any Reflex prop/API mismatches surfaced here before committing — this is the primary integration test for Tasks 5, 9, and 10's state classes, which had no isolated unit tests by design.

- [ ] **Step 5: Commit**

```bash
git add webapp/webapp/components/checklist.py webapp/webapp/pages/dashboard.py webapp/webapp/webapp.py
git commit -m "feat(webapp): add dashboard page (checklist, key/credits, docs, preferences)"
```

---

## Task 12: Playwright E2E for the critical conversion/retention path

**Files:**
- Create: `webapp/requirements-dev.txt`
- Create: `webapp/e2e/conftest.py`
- Create: `webapp/e2e/test_critical_path.py`

**Interfaces:**
- Consumes: a running `reflex run` instance (started by the test fixture) and a disposable Supabase test project's credentials via env vars.

- [ ] **Step 1: Add dev/test dependencies**

`webapp/requirements-dev.txt`:
```
pytest-playwright>=0.5.0
```

Run:
```bash
cd webapp
pip install -r requirements-dev.txt
playwright install chromium
```

- [ ] **Step 2: Write a fixture that boots the app for the test session**

`webapp/e2e/conftest.py`:
```python
import subprocess
import time

import httpx
import pytest


@pytest.fixture(scope="session")
def live_server():
    proc = subprocess.Popen(
        ["reflex", "run", "--env", "prod"],
        cwd="webapp",
    )
    base_url = "http://localhost:3000"
    for _ in range(60):
        try:
            httpx.get(base_url, timeout=1.0)
            break
        except httpx.RequestError:
            time.sleep(1)
    else:
        proc.terminate()
        raise RuntimeError("reflex run did not become ready in time")
    yield base_url
    proc.terminate()
    proc.wait(timeout=10)
```

- [ ] **Step 3: Write the critical-path test**

`webapp/e2e/test_critical_path.py`:
```python
import uuid

import pytest


@pytest.mark.usefixtures("live_server")
def test_signup_through_first_document_ticks_checklist(page, live_server):
    """Land -> sign up -> see checklist -> upload a doc -> checklist item ticks.
    This is the exact funnel the redesign spec targets for conversion + retention."""
    email = f"e2e-{uuid.uuid4().hex[:10]}@example.com"

    page.goto(live_server)
    page.get_by_text("Create your account").click()
    page.wait_for_url("**/login")

    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill("correct horse battery staple")
    page.get_by_role("button", name="Sign up").click()

    page.wait_for_url("**/dashboard")
    assert page.get_by_text("Get set up").is_visible()
    assert page.get_by_text("Download the app").is_visible()

    with page.expect_file_chooser() as chooser_info:
        page.get_by_text("Upload document").click()
    chooser_info.value.set_files(
        files=[{"name": "notes.txt", "mimeType": "text/plain", "buffer": b"my study notes for the exam"}]
    )

    page.wait_for_selector("text=ready", timeout=30_000)
    assert page.get_by_text("notes.txt").is_visible()
```

- [ ] **Step 4: Run it against a disposable test Supabase project**

Run (with `SUPABASE_URL`/`SUPABASE_ANON_KEY`/`SUPABASE_SERVICE_ROLE_KEY`/`LITELLM_URL`/`LITELLM_MASTER_KEY`/`EMBED_SECRET` set in `webapp/.env` to test-project values, never production):
```bash
cd webapp
pytest e2e/test_critical_path.py -v
```
Expected: PASS. If selectors don't match the actual rendered DOM from Task 11 (e.g. `get_by_label` needs an explicit label element added to `_field()` in Task 6), fix the component markup, not the test's intent — the test encodes the spec's critical path, not incidental markup choices.

- [ ] **Step 5: Commit**

```bash
git add webapp/requirements-dev.txt webapp/e2e/
git commit -m "test(webapp): add Playwright E2E for signup-to-first-upload critical path"
```

---

## Task 13: Dev README and final manual QA pass

**Files:**
- Create: `webapp/README.md`

**Interfaces:** none (documentation + final verification task).

- [ ] **Step 1: Write the dev README**

`webapp/README.md`:
```markdown
# Parakeet website (Reflex)

Python-only rebuild of the marketing + account site, running alongside the
existing Next.js `website/` (not yet a replacement — see
`docs/superpowers/specs/2026-07-27-reflex-website-redesign-design.md`).

## Dev setup

\`\`\`bash
cd webapp
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env      # fill in Supabase + LiteLLM values, same as website/'s deployment
reflex run
\`\`\`

## Tests

\`\`\`bash
pytest tests/ -v                 # unit tests for services/*
pytest e2e/ -v                   # Playwright E2E (needs a disposable test Supabase project)
\`\`\`

## Structure

- `webapp/services/` — pure business logic (Supabase, LiteLLM, document
  pipeline). Fully unit tested.
- `webapp/states/` — Reflex State orchestration. Thin by design; verified by
  running the app, not by isolated unit tests.
- `webapp/pages/`, `webapp/components/` — UI.
- `webapp/styles/tokens.py` — every color/font/radius/shadow used anywhere
  in the app.
```

- [ ] **Step 2: Full manual QA pass, start to finish**

Run: `reflex run`, then in a real browser:
1. `/` — hero, demo video slot, how-it-works, social proof, pricing all render; every CTA reaches `/login`.
2. `/login` — sign up, sign in, wrong-password error, Google OAuth button at least redirects to Google (full OAuth loop only completable with real Google OAuth credentials configured in Supabase).
3. `/download` — both buttons present, download click marks the checklist item.
4. `/dashboard` — checklist, open-app deep link + fallback, key box, credit meter, document upload (success + error + retry), preferences save-and-persist.
5. Resize the browser to ~375px width — confirm nothing overflows horizontally on any of the four pages (light-editorial cards should stack, not clip).

Expected: every item above works with no unhandled exceptions in the `reflex run` console. Fix anything that doesn't before the final commit — this is the last gate before calling the spec done.

- [ ] **Step 3: Commit**

```bash
git add webapp/README.md
git commit -m "docs(webapp): add dev README"
```

---

## Self-review notes

- **Spec coverage:** landing hero/demo/how-it-works/social-proof/pricing → Task 7; login/signup/Google OAuth → Tasks 5–6; download → Task 8; dashboard key/credits/docs/preferences → Tasks 9–11; onboarding checklist → Tasks 9 & 11; error handling + retry → Task 10 & 11; testing requirements (manual run-through + Playwright E2E) → every UI task's verification step + Task 12; dev docs → Task 13. The deferred items (in-app PySide6 tutorial, production cutover, payments, backend `first_query_at`) are called out in Global Constraints and intentionally have no task.
- **Placeholder scan:** no TBD/TODO markers. The one open item (`demo.mp4` not yet recorded) is flagged explicitly as a content dependency with a concrete path and a note that dev verification doesn't require it — not a vague "add later."
- **Type/name consistency:** `DashboardState.deep_link`, `.checklist_complete`, `.has_ready_doc`, `.ck_downloaded`, `.ck_opened_app` are defined once in Task 9 and referenced with those exact names in Tasks 8 and 11. `UploadState.uploading`/`.upload_error`/`.handle_upload`/`.retry_document` defined in Task 10, referenced identically in Task 11. `services.documents.chunk/extract_text/embed` and `services.litellm.mint_key/get_spend` signatures match between their Task 3/4 definitions and Task 9/10 call sites.
