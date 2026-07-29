import reflex as rx

from webapp.states.auth_state import AuthState
from webapp.styles import tokens


def nav() -> rx.Component:
    return rx.hstack(
        rx.link(
            rx.hstack(
                rx.box(
                    width="9px", height="9px", border_radius="999px",
                    background=tokens.BAND["mint_tag_text"],
                ),
                rx.text(tokens.BRAND_NAME, weight="bold", size="4", color=tokens.COLOR["text"]),
                spacing="2", align="center",
            ),
            href="/", text_decoration="none",
        ),
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            rx.link("Dashboard", href="/dashboard", color=tokens.COLOR["text"]),
            rx.hstack(
                rx.link("Log in", href="/login", color=tokens.COLOR["text_muted"]),
                rx.link(
                    "Get started", href="/login",
                    background=tokens.COLOR["accent"], color="white",
                    padding="10px 18px", border_radius=tokens.RADIUS["pill"],
                    text_decoration="none",
                ),
                spacing="4",
            ),
        ),
        width="100%", max_width="1040px", margin="0 auto",
        padding="16px 24px", align="center",
    )
