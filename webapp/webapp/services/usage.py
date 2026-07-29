"""Usage ledger service: session counting + trial cap enforcement.

Mirrors the Next.js API endpoints at website/app/api/usage/* for the
Reflex webapp. Called by the LiteLLM proxy or the desktop app's hosted
mode flow."""

from __future__ import annotations

import os
from typing import Any

import httpx

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
LITELLM_URL = os.environ.get("LITELLM_URL", "")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")


def _resolve_user_from_key(token: str) -> str | None:
    """Resolve a LiteLLM virtual key to a user_id via metadata."""
    try:
        resp = httpx.get(
            f"{LITELLM_URL}/key/info",
            params={"key": token},
            headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
            timeout=10,
        )
        if resp.status_code >= 400:
            return None
        info = resp.json().get("info", resp.json())
        return (info.get("metadata") or {}).get("user_id")
    except Exception:
        return None


def check_session(token: str) -> dict[str, Any]:
    """Check if the user behind `token` can start a session."""
    user_id = _resolve_user_from_key(token)
    if not user_id:
        return {"can_start": True, "tier": "unknown", "session_count": 0, "trial_remaining": 0}

    try:
        resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/check_session",
            json={"p_user_id": user_id},
            headers={
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code >= 400:
            return {"can_start": True, "tier": "unknown", "session_count": 0, "trial_remaining": 0}
        return resp.json()
    except Exception:
        return {"can_start": True, "tier": "unknown", "session_count": 0, "trial_remaining": 0}


def report_session_start(token: str, session_id: str) -> dict[str, Any]:
    """Report a session start. Returns {ok: true} or {error: "trial_limit_reached"}."""
    user_id = _resolve_user_from_key(token)
    if not user_id:
        return {"ok": True}

    try:
        supabase_headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        # Get current profile
        profile_resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            params={"id": f"eq.{user_id}"},
            headers=supabase_headers,
            timeout=10,
        )
        if profile_resp.status_code >= 400:
            return {"ok": True}

        profiles = profile_resp.json()
        if not profiles:
            return {"ok": True}

        profile = profiles[0]
        tier = profile.get("tier", "free")
        trial_used = profile.get("trial_used", False)
        session_count = profile.get("session_count", 0)

        is_trial = (tier == "trial") or (tier == "free" and not trial_used)

        if is_trial and session_count >= 1:
            return {"error": "trial_limit_reached"}

        # Insert usage ledger row
        insert_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/usage_ledger",
            json={
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "session_start",
                "tier": "trial" if is_trial else tier,
            },
            headers=supabase_headers,
            timeout=10,
        )
        if insert_resp.status_code >= 400:
            return {"ok": True}  # non-critical; let through

        # Update profile: mark trial_used and increment session_count
        update_data = {"session_count": session_count + 1}
        if tier == "free" and not trial_used:
            update_data["trial_used"] = True

        httpx.patch(
            f"{SUPABASE_URL}/rest/v1/profiles",
            params={"id": f"eq.{user_id}"},
            json=update_data,
            headers=supabase_headers,
            timeout=10,
        )

        return {"ok": True}
    except Exception:
        return {"ok": True}
