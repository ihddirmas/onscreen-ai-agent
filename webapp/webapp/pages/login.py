import reflex as rx

from webapp.states.auth_state import AuthState
from webapp.styles import tokens


def _field(label: str, name: str, type_: str = "text") -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", color=tokens.COLOR["text_muted"]),
        rx.input(name=name, type=type_, required=True, width="100%"),
        width="100%",
        spacing="1",
        align_items="start",
    )


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.text(f"🦜 {tokens.BRAND_NAME}", weight="bold", size="5"),
            rx.box(
                rx.heading("Log in or create your account", size="4", margin_bottom="16px"),
                # Two independent forms rather than one form with two submit
                # targets — this installed Reflex version (0.9.7) has no
                # rx.form_data() to read a form's fields outside its own
                # on_submit, so a "Sign up" button living inside the sign-in
                # form has no way to grab that form's values on click. Each
                # button submits its own form via on_submit instead.
                rx.form(
                    _field("Email", "email", "email"),
                    _field("Password", "password", "password"),
                    rx.button(
                        rx.cond(AuthState.busy, "…", "Log in"),
                        type="submit",
                        disabled=AuthState.busy,
                        background=tokens.COLOR["accent"],
                        color="white",
                        border_radius=tokens.RADIUS["pill"],
                        margin_top="12px",
                        width="100%",
                    ),
                    on_submit=AuthState.sign_in,
                    width="100%",
                ),
                rx.form(
                    _field("Email", "email", "email"),
                    _field("Password", "password", "password"),
                    rx.button(
                        rx.cond(AuthState.busy, "…", "Sign up"),
                        type="submit",
                        disabled=AuthState.busy,
                        variant="outline",
                        border_radius=tokens.RADIUS["pill"],
                        margin_top="12px",
                        width="100%",
                    ),
                    on_submit=AuthState.sign_up,
                    width="100%",
                    margin_top="8px",
                ),
                rx.button(
                    "Continue with Google",
                    on_click=AuthState.sign_in_with_google,
                    variant="outline",
                    width="100%",
                    margin_top="12px",
                    border_radius=tokens.RADIUS["pill"],
                ),
                rx.cond(
                    AuthState.error != "",
                    rx.text(AuthState.error, color=tokens.COLOR["error"], size="2", margin_top="10px"),
                ),
                background=tokens.COLOR["surface"],
                border=f"1px solid {tokens.COLOR['border']}",
                border_radius=tokens.RADIUS["md"],
                box_shadow=tokens.SHADOW_CARD,
                padding="28px",
                width="380px",
            ),
            spacing="5",
            align="center",
        ),
        min_height="100vh",
        background=tokens.COLOR["bg"],
    )
