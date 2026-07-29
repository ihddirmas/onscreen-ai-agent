import reflex as rx

from webapp.states.payment_state import PaymentState
from webapp.styles import tokens

_FREE_FEATURES = [
    "On-screen AI overlay",
    "Voice + screenshot answers",
    "~$1 of hosted model credits / month",
    "1 reference document",
]

_PRO_FEATURES = [
    "Everything in Free",
    "~$15 of hosted model credits / month",
    "Unlimited reference documents",
    "Priority models (Claude / GPT)",
]


def _tier_card(
    *, badge: str, name: str, price: str, features: list[str], cta: rx.Component,
    highlight: bool = False,
) -> rx.Component:
    return rx.vstack(
        rx.badge(badge, color_scheme="iris" if highlight else "gray"),
        rx.heading(name, size="5", font_family=tokens.FONT["serif"]),
        rx.hstack(
            rx.text(price, size="8", weight="bold"),
            rx.text("/ mo", color=tokens.COLOR["text_muted"], size="2"),
            align="baseline", spacing="1",
        ),
        *[rx.text(f"· {f}", size="2", color=tokens.COLOR["text_muted"]) for f in features],
        cta,
        background=tokens.COLOR["surface"],
        # Green, not violet — the same accent family as the real desktop
        # overlay's border (parakeet/ui/theme.py's accent_border), so the
        # one place on the pricing section meant to draw the eye ties back
        # to the actual product rather than an arbitrary decorative color.
        border=(
            f"2px solid {tokens.BAND['mint_tag_text']}" if highlight
            else f"1px solid {tokens.COLOR['border']}"
        ),
        border_radius=tokens.RADIUS["md"],
        box_shadow=tokens.SHADOW_FLOAT if highlight else tokens.SHADOW_CARD,
        padding="24px", width="260px", align="start", spacing="2",
        transition="transform 0.15s ease",
        _hover={"transform": "translateY(-4px)"},
    )


def pricing() -> rx.Component:
    return rx.vstack(
        rx.heading("Pricing", size="6", text_align="center", font_family=tokens.FONT["serif"]),
        rx.text(
            "Credits are metered by actual model usage. No API key needed — "
            "hosted access starts the moment you sign up.",
            color=tokens.COLOR["text_muted"], size="2", text_align="center",
        ),
        rx.hstack(
            _tier_card(
                badge="Get started",
                name="Free",
                price="$0",
                features=_FREE_FEATURES,
                cta=rx.link(
                    "Start free", href="/login",
                    background=tokens.COLOR["accent"], color="white",
                    padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                    text_decoration="none", margin_top="12px",
                ),
            ),
            _tier_card(
                badge="Most popular",
                name="Pro",
                price="$9",
                features=_PRO_FEATURES,
                highlight=True,
                cta=rx.vstack(
                    rx.button(
                        "Subscribe to Pro",
                        on_click=PaymentState.start_checkout("razorpay"),
                        background=tokens.COLOR["accent"], color="white",
                        padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                        margin_top="12px", cursor="pointer", border="none",
                    ),
                    rx.link(
                        "Pay by card instead (Stripe)",
                        on_click=PaymentState.start_checkout("stripe"),
                        color=tokens.COLOR["text_muted"], size="1",
                        text_decoration="underline", cursor="pointer",
                    ),
                    rx.cond(
                        PaymentState.checkout_error != "",
                        rx.text(
                            PaymentState.checkout_error,
                            color=tokens.COLOR["warning"], size="1",
                            max_width="220px",
                        ),
                    ),
                    spacing="2", align="start",
                ),
            ),
            spacing="5", justify="center", margin_top="20px",
        ),
        padding="24px", max_width="1040px", margin="0 auto",
    )
