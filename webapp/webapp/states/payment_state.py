"""Pricing-page checkout initiation — wired to the real Stripe + Razorpay
payments backend (``webapp/webapp/services/payments.py`` + webhook routes).
"""
from __future__ import annotations

import reflex as rx

from webapp.services.payments import create_razorpay_subscription, create_stripe_checkout_session
from webapp.states.auth_state import AuthState


class PaymentState(AuthState):
    checkout_error: str = ""
    checkout_busy: bool = False

    def start_checkout(self, provider: str = "razorpay"):
        """Kick off Pro-tier checkout. `provider` is "razorpay" or "stripe"."""
        if not self.is_logged_in:
            return rx.redirect("/login")
        self.checkout_error = ""
        self.checkout_busy = True
        try:
            if provider == "stripe":
                origin = self.router.url.origin
                url = create_stripe_checkout_session(
                    user_id=self.user_id,
                    success_url=f"{origin}/dashboard?checkout=success",
                    cancel_url=f"{origin}/?checkout=cancelled",
                    customer_email=self.email or None,
                )
            else:
                subscription = create_razorpay_subscription(user_id=self.user_id)
                url = subscription.get("short_url")
                if not url:
                    raise RuntimeError("Razorpay did not return a checkout URL")
        except Exception as exc:  # noqa: BLE001 - surfaced to the user, never swallowed
            self.checkout_error = f"Couldn't start checkout: {exc}"
            self.checkout_busy = False
            return
        self.checkout_busy = False
        return rx.redirect(url)
