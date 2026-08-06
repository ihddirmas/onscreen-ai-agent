import reflex as rx

from webapp.states.login_state import LoginState
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
                rx.heading(
                    rx.cond(LoginState.mode == "in", "Log in", "Create your account"),
                    size="4",
                    margin_bottom="16px",
                ),
                # One form, mode toggled via LoginState.mode — mirrors
                # website/app/login/page.tsx's single-form + mode-switch
                # pattern. The installed Reflex version (0.9.7) has no
                # rx.form_data() to read a form's fields outside its own
                # on_submit, so LoginState.submit() dispatches to sign_in/
                # sign_up based on the current mode rather than needing two
                # separate forms (which rendered as visibly duplicated
                # email/password fields — confusing, not the intent).
                rx.form(
                    _field("Email", "email", "email"),
                    _field("Password", "password", "password"),
                    rx.button(
                        rx.cond(
                            LoginState.busy,
                            "…",
                            rx.cond(LoginState.mode == "in", "Log in", "Sign up"),
                        ),
                        type="submit",
                        disabled=LoginState.busy,
                        background=tokens.COLOR["accent"],
                        color="white",
                        border_radius=tokens.RADIUS["pill"],
                        margin_top="12px",
                        width="100%",
                    ),
                    on_submit=LoginState.submit,
                    width="100%",
                ),
                rx.button(
                    "Continue with Google",
                    on_click=LoginState.sign_in_with_google,
                    variant="outline",
                    width="100%",
                    margin_top="12px",
                    border_radius=tokens.RADIUS["pill"],
                ),
                rx.cond(
                    LoginState.error != "",
                    rx.text(LoginState.error, color=tokens.COLOR["error"], size="2", margin_top="10px"),
                ),
                rx.hstack(
                    rx.text(
                        rx.cond(LoginState.mode == "in", "No account?", "Already have one?"),
                        color=tokens.COLOR["text_muted"], size="2",
                    ),
                    rx.link(
                        rx.cond(LoginState.mode == "in", "Sign up", "Log in"),
                        on_click=LoginState.toggle_mode,
                        cursor="pointer", size="2",
                    ),
                    spacing="1", margin_top="12px", justify="center",
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
