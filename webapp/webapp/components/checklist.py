import reflex as rx

from webapp.states.dashboard_state import DashboardState
from webapp.styles import tokens


def _item(done: rx.Var, label: str) -> rx.Component:
    return rx.hstack(
        rx.cond(
            done,
            rx.text("✓", color=tokens.COLOR["success"]),
            rx.text("○", color=tokens.COLOR["text_muted"]),
        ),
        rx.text(
            label,
            color=tokens.COLOR["text"],
            text_decoration=rx.cond(done, "line-through", "none"),
        ),
        spacing="2",
    )


def onboarding_checklist() -> rx.Component:
    return rx.cond(
        DashboardState.checklist_complete,
        rx.fragment(),
        rx.box(
            rx.heading("Get set up", size="4", margin_bottom="10px"),
            rx.vstack(
                _item(DashboardState.ck_downloaded, "Download the app"),
                _item(DashboardState.ck_opened_app, "Open the OnCUE app"),
                _item(DashboardState.has_ready_doc, "Upload a reference document"),
                spacing="2",
                align="start",
            ),
            background=tokens.COLOR["accent_soft"],
            border=f"1px solid {tokens.COLOR['border']}",
            border_radius=tokens.RADIUS["md"],
            padding="20px",
            margin_bottom="18px",
        ),
    )
