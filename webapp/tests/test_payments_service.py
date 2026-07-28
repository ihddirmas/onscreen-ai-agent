import hashlib
import hmac
import time

import pytest
import stripe
from postgrest.exceptions import APIError

from webapp.services import payments


# ---------------------------------------------------------------------------
# Fakes for the Supabase admin client's fluent query builder
# ---------------------------------------------------------------------------


class _Result:
    def __init__(self, data=None):
        self.data = data


class _FakeQuery:
    """Mimics postgrest's chainable builder: .select/.insert/.update/.eq/
    .maybe_single all return self; .execute() calls back into the handler
    the test configured for this table."""

    def __init__(self, on_execute):
        self._on_execute = on_execute
        self.payload = None

    def select(self, *_a, **_kw):
        return self

    def insert(self, payload):
        self.payload = payload
        return self

    def update(self, payload):
        self.payload = payload
        return self

    def eq(self, *_a, **_kw):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        return self._on_execute(self)


class _FakeClient:
    def __init__(self, handlers: dict):
        self._handlers = handlers
        self.calls: list[tuple[str, dict | None]] = []

    def table(self, name: str):
        handler = self._handlers[name]

        def _tracked(query: _FakeQuery):
            self.calls.append((name, query.payload))
            return handler(query)

        return _FakeQuery(_tracked)


def _stripe_sign(payload: bytes, secret: str, timestamp: int) -> str:
    signed_payload = f"{timestamp}.".encode() + payload
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


# ---------------------------------------------------------------------------
# Signature verification — real cryptographic round trips, nothing mocked
# ---------------------------------------------------------------------------


def test_verify_stripe_signature_accepts_valid_signature(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    payload = (
        b'{"id": "evt_1", "object": "event", "type": "checkout.session.completed", '
        b'"data": {"object": {}}}'
    )
    header = _stripe_sign(payload, "whsec_test_secret", int(time.time()))

    event = payments.verify_stripe_signature(payload, header)

    assert event["id"] == "evt_1"
    assert event["type"] == "checkout.session.completed"


def test_verify_stripe_signature_rejects_wrong_secret(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    payload = b'{"id": "evt_1"}'
    header = _stripe_sign(payload, "wrong_secret", int(time.time()))

    with pytest.raises(stripe.SignatureVerificationError):
        payments.verify_stripe_signature(payload, header)


def test_verify_stripe_signature_rejects_tampered_payload(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    original = b'{"id": "evt_1", "amount": 100}'
    header = _stripe_sign(original, "whsec_test_secret", int(time.time()))
    tampered = b'{"id": "evt_1", "amount": 999999}'

    with pytest.raises(stripe.SignatureVerificationError):
        payments.verify_stripe_signature(tampered, header)


def test_verify_razorpay_signature_accepts_valid_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "rzp_test_secret")
    body = b'{"event": "subscription.activated"}'
    signature = hmac.new(b"rzp_test_secret", body, hashlib.sha256).hexdigest()

    assert payments.verify_razorpay_signature(body, signature) is True


def test_verify_razorpay_signature_rejects_wrong_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "rzp_test_secret")
    body = b'{"event": "subscription.activated"}'

    assert payments.verify_razorpay_signature(body, "0" * 64) is False


def test_verify_razorpay_signature_rejects_missing_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "rzp_test_secret")

    assert payments.verify_razorpay_signature(b"{}", "") is False


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def test_record_event_once_processes_first_time_and_skips_replay(monkeypatch):
    seen: set[tuple[str, str]] = set()

    def payment_events_handler(query: _FakeQuery):
        key = (query.payload["provider"], query.payload["event_id"])
        if key in seen:
            raise APIError(
                {"code": "23505", "message": "duplicate key value violates unique constraint"}
            )
        seen.add(key)
        return _Result(None)

    client = _FakeClient({"payment_events": payment_events_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    first = payments.record_event_once("stripe", "evt_1", "checkout.session.completed", {"id": "evt_1"})
    second = payments.record_event_once("stripe", "evt_1", "checkout.session.completed", {"id": "evt_1"})

    assert first is True
    assert second is False
    assert len(client.calls) == 2


def test_record_event_once_reraises_non_conflict_errors(monkeypatch):
    def payment_events_handler(_query: _FakeQuery):
        raise APIError({"code": "42501", "message": "permission denied"})

    client = _FakeClient({"payment_events": payment_events_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    with pytest.raises(APIError):
        payments.record_event_once("stripe", "evt_1", "checkout.session.completed", {})


def test_handle_stripe_event_skips_processing_on_replay(monkeypatch):
    seen: set[tuple[str, str]] = set()

    def payment_events_handler(query: _FakeQuery):
        key = (query.payload["provider"], query.payload["event_id"])
        if key in seen:
            raise APIError({"code": "23505", "message": "dup"})
        seen.add(key)
        return _Result(None)

    def profiles_handler(_query: _FakeQuery):
        return _Result(None)

    client = _FakeClient({"payment_events": payment_events_handler, "profiles": profiles_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    activated_calls = []
    monkeypatch.setattr(
        payments, "handle_subscription_activated", lambda user_id, provider: activated_calls.append((user_id, provider))
    )

    event = {
        "id": "evt_1",
        "type": "checkout.session.completed",
        "data": {"object": {"client_reference_id": "user-1", "customer": "cus_1", "subscription": "sub_1"}},
    }

    payments.handle_stripe_event(event)
    payments.handle_stripe_event(event)  # replay

    assert activated_calls == [("user-1", "stripe")]


# ---------------------------------------------------------------------------
# "Don't re-mint if key exists" — the critical correctness rule
# ---------------------------------------------------------------------------


def test_activation_reuses_existing_key_instead_of_reminting(monkeypatch):
    def profiles_handler(query: _FakeQuery):
        if query.payload is None:  # select branch
            return _Result({"litellm_key": "sk-existing-user-key"})
        return _Result(None)  # update branch

    client = _FakeClient({"profiles": profiles_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    update_calls = []
    monkeypatch.setattr(payments, "update_key_budget", lambda key, tier: update_calls.append((key, tier)))

    def _mint_should_not_be_called(*_a, **_kw):
        raise AssertionError("mint_key must not be called when a litellm_key already exists")

    monkeypatch.setattr(payments, "mint_key", _mint_should_not_be_called)

    payments.handle_subscription_activated("user-1", "stripe")

    assert update_calls == [("sk-existing-user-key", "pro")]
    update_payload = client.calls[-1][1]
    assert update_payload["tier"] == "pro"
    assert update_payload["litellm_key"] == "sk-existing-user-key"
    assert update_payload["billing_provider"] == "stripe"


def test_activation_mints_new_key_when_none_exists(monkeypatch):
    def profiles_handler(query: _FakeQuery):
        if query.payload is None:  # select branch
            return _Result(None)
        return _Result(None)  # update branch

    client = _FakeClient({"profiles": profiles_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    mint_calls = []
    monkeypatch.setattr(payments, "mint_key", lambda user_id, tier: mint_calls.append((user_id, tier)) or "sk-new-key")

    def _update_should_not_be_called(*_a, **_kw):
        raise AssertionError("update_key_budget must not be called when there is no existing key")

    monkeypatch.setattr(payments, "update_key_budget", _update_should_not_be_called)

    payments.handle_subscription_activated("user-2", "razorpay")

    assert mint_calls == [("user-2", "pro")]
    update_payload = client.calls[-1][1]
    assert update_payload["litellm_key"] == "sk-new-key"
    assert update_payload["billing_provider"] == "razorpay"


def test_cancellation_shrinks_budget_on_existing_key(monkeypatch):
    def profiles_handler(query: _FakeQuery):
        if query.payload is None:
            return _Result({"litellm_key": "sk-existing"})
        return _Result(None)

    client = _FakeClient({"profiles": profiles_handler})
    monkeypatch.setattr(payments, "admin_client", lambda: client)

    update_calls = []
    monkeypatch.setattr(payments, "update_key_budget", lambda key, tier: update_calls.append((key, tier)))

    payments.handle_subscription_cancelled("user-1", "stripe")

    assert update_calls == [("sk-existing", "free")]
    update_payload = client.calls[-1][1]
    assert update_payload["tier"] == "free"
    assert update_payload["subscription_status"] == "canceled"
