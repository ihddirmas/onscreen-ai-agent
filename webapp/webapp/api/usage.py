"""Usage ledger API routes for the Reflex webapp.

These mirror the Next.js /api/usage/* endpoints so the desktop app's
hosted mode can report to either backend. Mounted on the FastAPI sub-app
in webapp.py alongside the webhook routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Request, Response

from webapp.services import usage as usage_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/usage/check")
async def usage_check(request: Request) -> Response:
    """Check if the user behind a LiteLLM token can start a session."""
    try:
        body = await request.json()
    except Exception:
        return Response(status_code=400)

    token = (body or {}).get("token")
    if not token:
        return Response(status_code=400)

    result = usage_service.check_session(token)
    import json
    return Response(
        content=json.dumps(result),
        media_type="application/json",
    )


@router.post("/api/usage/report")
async def usage_report(request: Request) -> Response:
    """Report a session_start or inference event to the usage ledger."""
    try:
        body = await request.json()
    except Exception:
        return Response(status_code=400)

    body = body or {}
    token = body.get("token")
    event_type = body.get("event_type")
    session_id = body.get("session_id")

    if not token or not event_type or not session_id:
        return Response(status_code=400)

    if event_type == "session_start":
        result = usage_service.report_session_start(token, session_id)
    elif event_type == "inference":
        result = usage_service.report_inference(
            token, session_id,
            model_used=body.get("model_used"),
            tokens_in=body.get("tokens_in", 0),
            tokens_out=body.get("tokens_out", 0),
        )
    else:
        return Response(status_code=400)

    import json
    status = 403 if result.get("error") == "trial_limit_reached" else 200
    return Response(
        content=json.dumps(result),
        status_code=status,
        media_type="application/json",
    )
