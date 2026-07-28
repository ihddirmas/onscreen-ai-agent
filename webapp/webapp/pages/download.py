"""Download page: a faithful parity port of website/app/download/page.tsx's
two-card pattern into the Reflex design system. Card 1 offers the desktop
app (Windows-only — there is no macOS build artifact in this repo). Card 2
explains that logging in mints a free hosted-trial license key
automatically, no payment or setup required, with a CTA to /login."""
import reflex as rx

from webapp.styles import tokens

_CARD_STYLE = {
    "background": tokens.COLOR["surface"],
    "border": f"1px solid {tokens.COLOR['border']}",
    "border_radius": tokens.RADIUS["md"],
    "box_shadow": tokens.SHADOW_CARD,
    "padding": "28px",
    "width": "100%",
    "max_width": "480px",
    "font_family": tokens.FONT["sans"],
}

_PRIMARY_LINK_STYLE = {
    "background": tokens.COLOR["accent"],
    "color": "white",
    "padding": "10px 18px",
    "border_radius": tokens.RADIUS["pill"],
    "text_decoration": "none",
    "font_family": tokens.FONT["sans"],
}


def _download_card() -> rx.Component:
    return rx.box(
        rx.heading(f"Download {tokens.BRAND_NAME}", size="5", color=tokens.COLOR["text"]),
        rx.text(
            f'Install the desktop app, then click "Open {tokens.BRAND_NAME} app" on '
            "your dashboard to sign in automatically.",
            color=tokens.COLOR["text_muted"],
            margin_bottom="16px",
        ),
        rx.hstack(
            rx.link("Windows (.exe)", href="#", **_PRIMARY_LINK_STYLE),
            rx.text(
                "macOS (soon)",
                color=tokens.COLOR["text_muted"],
                padding="10px 4px",
            ),
            spacing="4",
        ),
        rx.link(
            "← Back to dashboard",
            href="/dashboard",
            margin_top="16px",
            display="block",
            color=tokens.COLOR["text_muted"],
        ),
        **_CARD_STYLE,
    )


def _hosted_key_card() -> rx.Component:
    return rx.box(
        rx.badge("Hosted cohort", color_scheme="gray"),
        rx.heading(
            "Want the meeting copilot without your own API key?",
            size="4",
            margin_top="10px",
            color=tokens.COLOR["text"],
        ),
        rx.text(
            f"Log in and {tokens.BRAND_NAME} mints a free license key for you "
            "automatically — no provider key, no separate signup. Paste it into "
            'Settings and pick "hosted" as your provider.',
            color=tokens.COLOR["text_muted"],
        ),
        rx.text(
            "Priority models and a larger usage budget (Pro) are opening to a "
            "limited first cohort as we finish billing — log in now and you'll "
            "be first in line when it's ready.",
            color=tokens.COLOR["text_muted"],
            margin_top="8px",
        ),
        rx.link(
            "Log in to get your free key",
            href="/login",
            margin_top="8px",
            display="inline-block",
            **_PRIMARY_LINK_STYLE,
        ),
        margin_top="16px",
        **_CARD_STYLE,
    )


def download_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            _download_card(),
            _hosted_key_card(),
            align="center",
            spacing="0",
            padding_y="60px",
        ),
        background=tokens.COLOR["bg"],
        min_height="100vh",
    )
