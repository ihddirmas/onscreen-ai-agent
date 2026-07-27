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
