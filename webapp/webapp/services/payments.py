"""Stripe + Razorpay subscriptions: checkout/subscription creation, webhook
signature verification, idempotent event processing, and the profile tier
flip. Server-only — mirrors the pattern in services/litellm.py and
services/supabase.py (pure functions, env-driven, admin Supabase client for
anything that must bypass RLS on behalf of a webhook caller with no user
session).

Schema note: profiles gained exactly four billing columns in
website/supabase/schema_payments.sql — stripe_customer_id,
stripe_subscription_id, subscription_status, billing_provider. There is no
separate razorpay_subscription_id column, so Razorpay subscription ids are
also stored in stripe_subscription_id (the column name predates the second
provider; billing_provider disambiguates which provider it belongs to).
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import razorpay
import stripe
from postgrest.exceptions import APIError

from webapp.services.litellm import get_spend, mint_key, update_key_budget
from webapp.services.supabase import admin_client

FREE_TIER = "free"
PRO_TIER = "pro"

# Razorpay subscription.create requires a total_count of billing cycles.
# There's no "until cancelled" option, so we use a long-running cap (10
# years of monthly cycles) and rely on subscription.cancelled webhooks /
# explicit cancellation to end it sooner.
_RAZORPAY_TOTAL_CYCLES = 120


# ---------------------------------------------------------------------------
# Env helpers
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


def _configure_stripe() -> None:
    stripe.api_key = _require_env("STRIPE_SECRET_KEY")


def _razorpay_client() -> razorpay.Client:
    key_id = _require_env("RAZORPAY_KEY_ID")
    key_secret = _require_env("RAZORPAY_KEY_SECRET")
    return razorpay.Client(auth=(key_id, key_secret))


def _as_plain_dict(obj: Any) -> Any:
    """Stripe events are StripeObject (Mapping-like, not JSON-serializable
    as-is). Plain dicts (used directly in tests) pass through unchanged."""
    to_dict = getattr(obj, "to_dict", None)
    return to_dict() if callable(to_dict) else obj


# ---------------------------------------------------------------------------
# Checkout / subscription creation
# ---------------------------------------------------------------------------


def create_stripe_checkout_session(
    user_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: str | None = None,
) -> str:
    """Create a Stripe Checkout Session for the Pro subscription price.
    Returns the hosted checkout URL to redirect the user to."""
    _configure_stripe()
    price_id = _require_env("STRIPE_PRICE_ID_PRO")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
        client_reference_id=user_id,
        subscription_data={"metadata": {"user_id": user_id}},
        metadata={"user_id": user_id},
    )
    return session.url


def create_razorpay_subscription(user_id: str) -> dict:
    """Create a Razorpay subscription for the Pro plan. Returns the API
    response — `short_url` is where the user completes UPI Autopay / card
    mandate setup."""
    client = _razorpay_client()
    plan_id = _require_env("RAZORPAY_PLAN_ID_PRO")
    return client.subscription.create(
        data={
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": _RAZORPAY_TOTAL_CYCLES,
            "notes": {"user_id": user_id},
        }
    )


# ---------------------------------------------------------------------------
# Webhook signature verification
# ---------------------------------------------------------------------------


def verify_stripe_signature(payload: bytes, sig_header: str) -> Any:
    """Verify + parse a raw Stripe webhook body. Raises
    stripe.SignatureVerificationError (bad/missing signature) or ValueError
    (malformed payload) on failure — callers should respond 400."""
    secret = _require_env("STRIPE_WEBHOOK_SECRET")
    # construct_event verifies the signature itself; it doesn't need
    # stripe.api_key set, but subsequent API calls in this module do.
    return stripe.Webhook.construct_event(payload, sig_header, secret)


def verify_razorpay_signature(payload: bytes, signature: str) -> bool:
    """Verify a Razorpay webhook's HMAC-SHA256 signature over the raw body.
    Never raises — returns False on any mismatch or missing signature so
    the route can respond with a clean 400."""
    if not signature:
        return False
    secret = _require_env("RAZORPAY_WEBHOOK_SECRET")
    body_str = payload.decode("utf-8")
    try:
        return razorpay.Utility().verify_webhook_signature(body_str, signature, secret)
    except razorpay.errors.SignatureVerificationError:
        return False


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def _is_unique_violation(exc: APIError) -> bool:
    return getattr(exc, "code", None) == "23505"


def record_event_once(provider: str, event_id: str, event_type: str, payload: Any) -> bool:
    """Insert (provider, event_id) into payment_events. Returns True the
    first time an event is seen (caller should process it), False on replay
    (unique-constraint hit — caller should skip processing, still return
    200 so the provider stops retrying)."""
    client = admin_client()
    try:
        client.table("payment_events").insert(
            {
                "provider": provider,
                "event_id": event_id,
                "type": event_type,
                "payload": _as_plain_dict(payload),
            }
        ).execute()
        return True
    except APIError as exc:
        if _is_unique_violation(exc):
            return False
        raise


# ---------------------------------------------------------------------------
# Shared activation / cancellation (called by both providers)
# ---------------------------------------------------------------------------


def handle_subscription_activated(user_id: str, provider: str) -> None:
    """Flip a profile to Pro. If the user already has a litellm_key, bump
    its budget/model allowlist in place instead of minting a new one —
    re-minting would orphan the key already written to the user's desktop
    config.env."""
    client = admin_client()
    existing = (
        client.table("profiles").select("litellm_key").eq("id", user_id).maybe_single().execute()
    )
    existing_key = (existing.data or {}).get("litellm_key") if existing.data else None

    if existing_key:
        update_key_budget(existing_key, PRO_TIER)
        key = existing_key
    else:
        key = mint_key(user_id, PRO_TIER)

    client.table("profiles").update(
        {
            "tier": PRO_TIER,
            "subscription_status": "active",
            "billing_provider": provider,
            "litellm_key": key,
        }
    ).eq("id", user_id).execute()


def handle_subscription_cancelled(user_id: str, provider: str) -> None:
    """Flip a profile back to Free and shrink the existing key's budget.
    The key itself is never revoked/reissued here, only its budget."""
    client = admin_client()
    existing = (
        client.table("profiles").select("litellm_key").eq("id", user_id).maybe_single().execute()
    )
    existing_key = (existing.data or {}).get("litellm_key") if existing.data else None

    if existing_key:
        update_key_budget(existing_key, FREE_TIER)

    client.table("profiles").update(
        {
            "tier": FREE_TIER,
            "subscription_status": "canceled",
            "billing_provider": provider,
        }
    ).eq("id", user_id).execute()


def _set_stripe_ids(user_id: str, customer_id: str | None, subscription_id: str | None) -> None:
    updates: dict[str, str] = {"billing_provider": "stripe"}
    if customer_id:
        updates["stripe_customer_id"] = customer_id
    if subscription_id:
        updates["stripe_subscription_id"] = subscription_id
    if len(updates) > 1:
        admin_client().table("profiles").update(updates).eq("id", user_id).execute()


def _set_razorpay_subscription_id(user_id: str, subscription_id: str | None) -> None:
    if not subscription_id:
        return
    admin_client().table("profiles").update(
        {"billing_provider": "razorpay", "stripe_subscription_id": subscription_id}
    ).eq("id", user_id).execute()


def _set_subscription_status(user_id: str, status: str) -> None:
    admin_client().table("profiles").update({"subscription_status": status}).eq(
        "id", user_id
    ).execute()


# ---------------------------------------------------------------------------
# Event dispatch
# ---------------------------------------------------------------------------

_STRIPE_ACTIVE_STATUSES = {"active", "trialing"}
_STRIPE_INACTIVE_STATUSES = {"canceled", "unpaid", "incomplete_expired"}


def handle_stripe_event(event: Any) -> None:
    """Dispatch a verified Stripe event. Idempotent: a replayed event_id is
    a no-op (record_event_once returns False and we skip straight out)."""
    event_id = event["id"]
    event_type = event["type"]
    if not record_event_once("stripe", event_id, event_type, event):
        return

    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data_object.get("client_reference_id") or (
            data_object.get("metadata") or {}
        ).get("user_id")
        if not user_id:
            return
        _set_stripe_ids(user_id, data_object.get("customer"), data_object.get("subscription"))
        handle_subscription_activated(user_id, "stripe")

    elif event_type == "customer.subscription.updated":
        user_id = (data_object.get("metadata") or {}).get("user_id")
        if not user_id:
            return
        status = data_object.get("status")
        if status in _STRIPE_ACTIVE_STATUSES:
            handle_subscription_activated(user_id, "stripe")
        elif status in _STRIPE_INACTIVE_STATUSES:
            handle_subscription_cancelled(user_id, "stripe")
        elif status:
            _set_subscription_status(user_id, status)

    elif event_type == "customer.subscription.deleted":
        user_id = (data_object.get("metadata") or {}).get("user_id")
        if not user_id:
            return
        handle_subscription_cancelled(user_id, "stripe")


def handle_razorpay_event(event: dict, event_id: str) -> None:
    """Dispatch a verified Razorpay event. `event_id` must come from the
    `x-razorpay-event-id` request header (unique per event per Razorpay's
    webhook docs) — the JSON payload itself carries no top-level event id."""
    if not event_id:
        raise ValueError("event_id is required for Razorpay webhook idempotency")

    event_type = event.get("event", "")
    if not record_event_once("razorpay", event_id, event_type, event):
        return

    subscription_entity = (
        (event.get("payload") or {}).get("subscription", {}).get("entity", {})
    )
    user_id = (subscription_entity.get("notes") or {}).get("user_id")
    if not user_id:
        return

    if event_type == "subscription.activated":
        _set_razorpay_subscription_id(user_id, subscription_entity.get("id"))
        handle_subscription_activated(user_id, "razorpay")
    elif event_type == "subscription.cancelled":
        handle_subscription_cancelled(user_id, "razorpay")


# ---------------------------------------------------------------------------
# Margin visibility (computed on demand, no ledger table)
# ---------------------------------------------------------------------------


def _stripe_revenue(customer_id: str | None, since: datetime) -> float:
    if not customer_id:
        return 0.0
    _configure_stripe()
    invoices = stripe.Invoice.list(
        customer=customer_id,
        status="paid",
        created={"gte": int(since.timestamp())},
        limit=100,
    )
    return sum(inv.amount_paid for inv in invoices.data) / 100


def _razorpay_revenue(subscription_id: str | None, since: datetime) -> float:
    if not subscription_id:
        return 0.0
    client = _razorpay_client()
    invoices = client.invoice.all(
        data={"subscription_id": subscription_id, "from": int(since.timestamp())}
    )
    paid_paise = sum(
        item.get("amount_paid", 0)
        for item in invoices.get("items", [])
        if item.get("status") == "paid"
    )
    return paid_paise / 100


def get_margin(user_id: str, since: datetime) -> dict:
    """revenue = completed Stripe invoices + Razorpay payments for this user
    in the period (queried live from each provider); cost = this user's
    cumulative LiteLLM key spend. No local ledger — computed on demand."""
    client = admin_client()
    profile = (
        client.table("profiles")
        .select("stripe_customer_id, stripe_subscription_id, litellm_key, billing_provider")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    info = profile.data or {} if profile else {}

    revenue = _stripe_revenue(info.get("stripe_customer_id"), since)
    if info.get("billing_provider") == "razorpay":
        revenue += _razorpay_revenue(info.get("stripe_subscription_id"), since)

    cost = 0.0
    litellm_key = info.get("litellm_key")
    if litellm_key:
        spend, _max_budget = get_spend(litellm_key)
        cost = spend

    return {"revenue": revenue, "cost": cost, "margin": revenue - cost}
