"""Optimus-inspired marketing landing (v0-style) for the Reflex webapp."""
import reflex as rx

from webapp.states.auth_state import AuthState
from webapp.states.payment_state import PaymentState
from webapp.styles import tokens

_MARQUEE = [
    ("1 hotkey", "replaces the alt-tab cycle", "DEVELOPERS"),
    ("Hinglish", "dictation at your cursor", "STUDENTS"),
    ("<1s", "to first token on screen", "CALLS"),
    ("Private", "invisible on screen share", "DEMOS"),
]

_FEATURES = [
    ("01", "Screen-aware answers",
     "Press a hotkey and ask about whatever is on your screen — errors, diagrams, slides. "
     "No screenshot → paste → alt-tab back."),
    ("02", "Hinglish-native dictation",
     "Hold a key and speak the way you actually talk. Text lands in WhatsApp, Gmail, "
     "or any focused field — no translating to English first."),
    ("03", "Grounded in your documents",
     "Upload your resume, notes, or study plan. Answers pull from your reference docs via RAG."),
    ("04", "Invisible when it matters",
     "The overlay stays off screen recordings and shares by default — private during demos and calls."),
]

_STEPS = [
    ("I", "Press your hotkey",
     "Ctrl+Shift+Space for screen Q&A, Ctrl+Shift+D to dictate, Ctrl+Shift+M during a call."),
    ("II", "OnCUE captures context",
     "A screenshot, your voice, or meeting audio — whichever mode you triggered."),
    ("III", "Answer streams on the overlay",
     "A floating transparent window with follow-ups, or text typed into your app."),
]


def _nav() -> rx.Component:
    return rx.box(
        rx.link(tokens.BRAND_NAME, href="/", class_name="opt-brand"),
        rx.hstack(
            rx.link("Features", href="#features"),
            rx.link("How it works", href="#how-it-works"),
            rx.link("Pricing", href="#pricing"),
            rx.cond(
                AuthState.is_logged_in,
                rx.link("Dashboard", href="/dashboard"),
                rx.fragment(
                    rx.link("Sign in", href="/login"),
                    rx.link("Get started", href="/login", class_name="opt-btn-primary"),
                ),
            ),
            spacing="6",
            align="center",
            class_name="opt-nav-links",
        ),
        class_name="opt-nav",
    )


def _marquee_track() -> rx.Component:
    items = []
    for stat, label, tag in _MARQUEE * 2:
        items.append(
            rx.box(
                rx.text(stat, class_name="opt-marquee-stat"),
                rx.box(
                    rx.text(label),
                    rx.text(tag, class_name="opt-marquee-tag"),
                    class_name="opt-marquee-meta",
                ),
                class_name="opt-marquee-item",
            )
        )
    return rx.box(rx.box(*items, class_name="opt-marquee"), class_name="opt-marquee-wrap")


def _hero() -> rx.Component:
    return rx.box(
        rx.box(class_name="opt-grid-bg"),
        rx.box(
            rx.text("The on-screen AI copilot", class_name="opt-label"),
            rx.vstack(
                rx.heading("Ask your screen.", class_name="opt-headline"),
                rx.heading("Skip the alt-tab.", class_name="opt-headline opt-headline-muted"),
                spacing="0",
                margin_bottom="3rem",
            ),
            rx.box(
                rx.text(
                    "Dictate in Hinglish, ask about anything visible, and get answers grounded "
                    "in your own documents — from a private overlay that stays off screen shares.",
                    class_name="opt-hero-sub",
                ),
                rx.box(
                    rx.link("Start free →", href="/login", class_name="opt-btn-primary"),
                    rx.link("See how it works", href="#how-it-works", class_name="opt-btn-secondary"),
                    class_name="opt-hero-ctas",
                ),
                class_name="opt-hero-grid",
            ),
            rx.box(
                rx.box(
                    rx.hstack(
                        rx.box(class_name="opt-dot red"),
                        rx.box(class_name="opt-dot yellow"),
                        rx.box(class_name="opt-dot green"),
                        rx.spacer(),
                        rx.text("Ctrl+Shift+Space", class_name="opt-overlay-bar"),
                    ),
                    rx.text("what's this error?", class_name="opt-overlay-q"),
                    rx.text(
                        "TypeError on line 42 — wrap with Number() at the call site.",
                        class_name="opt-overlay-a",
                    ),
                    class_name="opt-overlay-mock",
                ),
                display="flex",
                justify_content="center",
                width="100%",
            ),
            position="relative",
            z_index="1",
        ),
        _marquee_track(),
        class_name="opt-hero",
    )


def _features() -> rx.Component:
    rows = []
    for num, title, body in _FEATURES:
        rows.append(
            rx.box(
                rx.text(num, class_name="opt-feature-num"),
                rx.box(
                    rx.heading(title, class_name="opt-feature-title"),
                    rx.text(body, class_name="opt-feature-body"),
                ),
                class_name="opt-feature-row",
            )
        )
    return rx.box(
        rx.box(
            rx.text("Capabilities", class_name="opt-label"),
            rx.vstack(
                rx.heading("Everything you need.", class_name="opt-section-title"),
                rx.heading(
                    "Nothing you don't.",
                    class_name="opt-section-title opt-headline-muted",
                ),
                spacing="0",
            ),
            margin_bottom="3rem",
        ),
        *rows,
        id="features",
        class_name="opt-section",
    )


def _process() -> rx.Component:
    steps = []
    for num, title, body in _STEPS:
        steps.append(
            rx.box(
                rx.text(num, class_name="opt-feature-num"),
                rx.heading(title, class_name="opt-feature-title", margin_top="1rem"),
                rx.text(body, class_name="opt-feature-body"),
                class_name="opt-step",
            )
        )
    return rx.box(
        rx.box(
            rx.text("Process", class_name="opt-label"),
            rx.vstack(
                rx.heading("Three steps.", class_name="opt-section-title"),
                rx.heading(
                    "Zero context switching.",
                    class_name="opt-section-title opt-headline-muted",
                ),
                spacing="0",
            ),
            max_width="1400px",
            margin="0 auto",
        ),
        rx.box(*steps, class_name="opt-steps"),
        rx.box(
            rx.text("oncue://connect", color="rgba(250,250,250,0.4)"),
            rx.text(
                "# One click from your dashboard — no API keys to paste\n"
                "oncue://connect?token=…&web=…&rag=…&backend=…",
                white_space="pre-wrap",
            ),
            class_name="opt-code-block",
        ),
        id="how-it-works",
        class_name="opt-dark-band",
    )


def _price_card(
    num: str, name: str, desc: str, price: str, features: list[str],
    highlight: bool, cta: rx.Component,
) -> rx.Component:
    card_class = "opt-price-card highlight" if highlight else "opt-price-card"
    return rx.box(
        rx.cond(highlight, rx.text("Most popular", class_name="opt-price-badge"), rx.fragment()),
        rx.text(num, class_name="opt-feature-num"),
        rx.heading(name, class_name="opt-feature-title"),
        rx.text(desc, font_size="0.875rem", opacity="0.7"),
        rx.hstack(
            rx.text(price, font_family=tokens.FONT["serif"], font_size="3rem"),
            rx.text("/month", font_size="0.875rem", opacity="0.6"),
            align="baseline",
            margin_top="1.5rem",
        ),
        rx.vstack(
            *[rx.text(f"— {f}", font_size="0.875rem") for f in features],
            align="start",
            spacing="2",
            margin_top="1.5rem",
        ),
        rx.box(cta, margin_top="2rem"),
        class_name=card_class,
    )


def _pricing() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text("Pricing", class_name="opt-label"),
            rx.heading("Simple, transparent pricing", class_name="opt-section-title"),
            rx.text(
                "Start free with hosted models. Upgrade when you need Claude, GPT, or Gemini.",
                color=tokens.COLOR["text_muted"],
                margin_top="1rem",
                text_align="center",
            ),
            text_align="center",
        ),
        rx.box(
            _price_card(
                "01", "Free", "For trying hosted mode", "$0",
                ["On-screen AI overlay", "Voice + screenshot answers",
                 "~$1 hosted credits / month", "1 reference document"],
                False,
                rx.link("Start free", href="/login", class_name="opt-btn-primary", width="100%"),
            ),
            _price_card(
                "02", "Pro", "For daily power users", "$9",
                ["Everything in Free", "~$15 hosted credits / month",
                 "Unlimited reference documents", "Claude, GPT & Gemini"],
                True,
                rx.vstack(
                    rx.button(
                        "Subscribe to Pro",
                        on_click=PaymentState.start_checkout("razorpay"),
                        class_name="opt-btn-primary",
                        width="100%",
                        cursor="pointer",
                    ),
                    rx.link(
                        "Pay by card (Stripe)",
                        on_click=PaymentState.start_checkout("stripe"),
                        font_size="0.75rem",
                        opacity="0.7",
                        cursor="pointer",
                    ),
                    rx.cond(
                        PaymentState.checkout_error != "",
                        rx.text(PaymentState.checkout_error, color=tokens.COLOR["warning"], size="1"),
                    ),
                    width="100%",
                    spacing="2",
                ),
            ),
            class_name="opt-pricing-grid",
        ),
        id="pricing",
        class_name="opt-section",
    )


def _cta() -> rx.Component:
    return rx.box(
        rx.heading("Ready to stay in flow?", class_name="opt-section-title"),
        rx.text(
            "Download the desktop app, sign in once, and press your first hotkey.",
            color=tokens.COLOR["text_muted"],
            margin_top="1rem",
        ),
        rx.hstack(
            rx.link("Start free", href="/login", class_name="opt-btn-primary"),
            rx.link("Download app", href="/download", class_name="opt-btn-secondary"),
            spacing="4",
            justify="center",
            margin_top="2.5rem",
            flex_wrap="wrap",
        ),
        rx.text("No API key required for hosted mode", font_size="0.875rem",
                color=tokens.COLOR["text_muted"], margin_top="1.5rem"),
        class_name="opt-cta-section",
    )


def optimus_landing_page() -> rx.Component:
    return rx.box(
        _nav(),
        _hero(),
        _features(),
        _process(),
        _pricing(),
        _cta(),
        rx.text(f"© {tokens.BRAND_NAME}", class_name="opt-footer"),
        class_name="opt-page",
    )
