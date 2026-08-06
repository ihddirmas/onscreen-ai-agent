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
