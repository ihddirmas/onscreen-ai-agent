"""Usage ledger client: desktop app reports session starts + inferences to the
hosted backend for trial cap enforcement and cost tracking."""

from __future__ import annotations

import json
import uuid
from typing import Any
from urllib.request import Request, urlopen

from oncue.config import get_config

SESSION_ID: str | None = None


def _session_id() -> str:
    global SESSION_ID
    if SESSION_ID is None:
        SESSION_ID = str(uuid.uuid4())
    return SESSION_ID


def _web_url() -> str | None:
    cfg = get_config()
    if cfg.provider != "hosted" or not cfg.web_url:
        return None
    return cfg.web_url.rstrip("/")


def _post(path: str, body: dict[str, Any]) -> dict[str, Any] | None:
    """POST to the Parakeet website API. Returns parsed JSON or None on failure."""
    base = _web_url()
    if not base:
        return None
    cfg = get_config()
    payload = {**body, "token": cfg.oncue_token}
    try:
        data = json.dumps(payload).encode()
        req = Request(f"{base}/api{path}", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def check_session() -> dict[str, Any]:
    """Check if the current user can start a session.
    Returns the API response dict or a default allow response if unreachable."""
    result = _post("/usage/check", {"session_id": _session_id()})
    if result is None:
        return {"can_start": True, "tier": "unknown", "session_count": 0, "trial_remaining": 0}
    return result


def report_session_start() -> bool:
    """Report a session start to the usage ledger. Returns True if allowed."""
    result = _post("/usage/report", {
        "session_id": _session_id(),
        "event_type": "session_start",
    })
    if result is None:
        return True  # offline — let through
    if result.get("error") == "trial_limit_reached":
        return False
    return result.get("ok", False)


def report_inference(model_used: str | None = None,
                     tokens_in: int = 0,
                     tokens_out: int = 0) -> None:
    """Report an inference event (best-effort, fire-and-forget)."""
    _post("/usage/report", {
        "session_id": _session_id(),
        "event_type": "inference",
        "model_used": model_used,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
    })
