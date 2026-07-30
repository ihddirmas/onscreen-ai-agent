"""Stripe + Razorpay webhook routes.

Reflex apps are WebSocket/State-driven — there is no browser session for a
server-to-server webhook call, so these are NOT Reflex State event
handlers. They're plain FastAPI routes mounted onto Reflex's escape-hatch
ASGI app in webapp.py.

Verified against the installed Reflex version (0.9.7): `rx.App()` exposes no
public `.api` property, only a private `_api` attribute, which is a plain
`starlette.applications.Starlette` instance (not FastAPI) — Starlette has no
`include_router`/`add_api_route`. So this module builds a small FastAPI app
around the router and webapp.py mounts *that* onto `app._api`, which works
because FastAPI apps are themselves valid ASGI sub-apps for Starlette's
`.mount()`.

Both handlers read the raw request body directly (`await request.body()`)
before any JSON parsing, since signature verification is computed over the
exact bytes the provider sent.
"""
from __future__ import annotations

import json
import logging

import stripe
from fastapi import APIRouter, Request, Response

from webapp.services import payments

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> Response:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = payments.verify_stripe_signature(payload, sig_header)
    except (stripe.SignatureVerificationError, ValueError) as exc:
        logger.warning("Rejected Stripe webhook: %s", exc)
        return Response(status_code=400)

    try:
        payments.handle_stripe_event(event)
    except Exception:
        logger.exception("Error handling Stripe webhook event %s", event.get("id"))
        return Response(status_code=500)

    return Response(status_code=200)


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request) -> Response:
    payload = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")

    if not payments.verify_razorpay_signature(payload, signature):
        logger.warning("Rejected Razorpay webhook: bad signature")
        return Response(status_code=400)

    # Unique per event per Razorpay's webhook docs — the JSON body itself
    # carries no top-level event id.
    event_id = request.headers.get("x-razorpay-event-id", "")
    if not event_id:
        logger.warning("Razorpay webhook missing x-razorpay-event-id header")
        return Response(status_code=400)

    try:
        event = json.loads(payload)
    except ValueError:
        return Response(status_code=400)

    try:
        payments.handle_razorpay_event(event, event_id)
    except Exception:
        logger.exception("Error handling Razorpay webhook event %s", event_id)
        return Response(status_code=500)

    return Response(status_code=200)
