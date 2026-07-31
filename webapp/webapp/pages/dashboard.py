"""Dashboard: key/credits, documents, preferences, onboarding checklist."""
import reflex as rx

from webapp.components.checklist import onboarding_checklist
from webapp.components.nav import nav
from webapp.states.dashboard_state import DashboardState
from webapp.states.upload_state import UploadState
from webapp.styles import tokens


def _card(*children, **style) -> rx.Component:
    return rx.box(
        *children,
        background=tokens.COLOR["surface"],
        border=f"1px solid {tokens.COLOR['border']}",
        border_radius=tokens.RADIUS["md"],
        box_shadow=tokens.SHADOW_CARD,
        padding="22px",
        margin_bottom="18px",
        **style,
    )


def _status_pill(status: rx.Var) -> rx.Component:
    color = rx.cond(
        status == "ready",
        tokens.COLOR["success"],
        rx.cond(status == "processing", tokens.COLOR["warning"], tokens.COLOR["error"]),
    )
    return rx.badge(status, color=color, variant="soft")


def _open_app_card() -> rx.Component:
    return _card(
        rx.heading(f"Use {tokens.BRAND_NAME} on your computer", size="4"),
        rx.text(
            "Launch the desktop app already signed in — no key to paste.",
            color=tokens.COLOR["text_muted"],
        ),
        rx.hstack(
            rx.link(
                f"Open {tokens.BRAND_NAME} app",
                href=DashboardState.deep_link,
                id="open-app-link",
                on_click=DashboardState.mark_opened_app,
                background=tokens.COLOR["accent"],
                color="white",
                padding="10px 18px",
                border_radius=tokens.RADIUS["pill"],
                text_decoration="none",
            ),
            rx.link(
                "Download the app",
                href="/download",
                on_click=DashboardState.mark_downloaded,
                color=tokens.COLOR["text"],
                padding="10px 18px",
                border_radius=tokens.RADIUS["pill"],
                text_decoration="none",
                border=f"1px solid {tokens.COLOR['border']}",
            ),
            spacing="4",
            margin_top="8px",
            flex_wrap="wrap",
        ),
        rx.box(
            "Didn't open? You may not have the app installed yet.",
            id="pk-fallback",
            display="none",
            color=tokens.COLOR["warning"],
            font_size="13px",
            margin_top="8px",
        ),
        rx.script("""
            document.addEventListener('DOMContentLoaded', () => {
              const link = document.getElementById('open-app-link');
              const fallback = document.getElementById('pk-fallback');
              if (!link || !fallback) return;
              link.addEventListener('click', () => {
                let hidden = false;
                const onBlur = () => { hidden = true; };
                window.addEventListener('blur', onBlur, { once: true });
                setTimeout(() => {
                  window.removeEventListener('blur', onBlur);
                  if (!hidden) fallback.style.display = 'block';
                }, 1500);
              });
            });
        """),
    )


def _key_and_credits_card() -> rx.Component:
    return rx.hstack(
        _card(
            rx.hstack(
                rx.heading(f"Your {tokens.BRAND_NAME} key", size="4"),
                rx.badge(DashboardState.tier),
                spacing="3",
                align="center",
            ),
            rx.text(
                "Paste this into the desktop app Settings if the deep link does not work.",
                color=tokens.COLOR["text_muted"],
                margin_top="6px",
            ),
            rx.cond(
                DashboardState.oncue_key != "",
                rx.hstack(
                    rx.code(
                        DashboardState.oncue_key,
                        font_family=tokens.FONT["mono"],
                        font_size="12px",
                        padding="10px",
                        background=tokens.COLOR["accent_soft"],
                        border_radius=tokens.RADIUS["sm"],
                        overflow_x="auto",
                        width="100%",
                    ),
                    rx.button(
                        DashboardState.copy_msg,
                        on_click=[
                            rx.set_clipboard(DashboardState.oncue_key),
                            DashboardState.copy_key,
                        ],
                        variant="outline",
                        flex_shrink="0",
                    ),
                    width="100%",
                    margin_top="10px",
                    align="start",
                ),
                rx.text(
                    "Key will appear once the backend is connected.",
                    color=tokens.COLOR["text_muted"],
                    margin_top="8px",
                ),
            ),
            width="100%",
        ),
        _card(
            rx.heading("Credit usage", size="4"),
            rx.progress(value=DashboardState.credit_pct, max=100, width="100%"),
            rx.text(
                DashboardState.spend_label,
                color=tokens.COLOR["text_muted"],
                size="2",
                margin_top="8px",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
        flex_direction=["column", "column", "row"],
    )


def _trial_card() -> rx.Component:
    return rx.cond(
        DashboardState.trial_remaining > 0,
        _card(
            rx.heading("Trial status", size="4"),
            rx.text(
                "You have ",
                DashboardState.trial_remaining,
                " trial session remaining on the free plan.",
                color=tokens.COLOR["text_muted"],
            ),
            rx.link(
                "View pricing",
                href="/#pricing",
                margin_top="8px",
                display="inline-block",
                color=tokens.COLOR["text"],
            ),
        ),
        rx.fragment(),
    )


def _documents_card() -> rx.Component:
    return _card(
        rx.heading("Reference documents", size="4"),
        rx.text(
            "Upload your resume, notes, or study plan. "
            f"{tokens.BRAND_NAME} uses them for better personalized answers.",
            color=tokens.COLOR["text_muted"],
        ),
        rx.upload(
            rx.button(
                rx.cond(UploadState.uploading, "Uploading…", "Upload document"),
                disabled=UploadState.uploading,
                margin_top="10px",
            ),
            id="doc_upload",
            max_files=1,
            accept={
                "application/pdf": [".pdf"],
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                "text/plain": [".txt"],
                "text/markdown": [".md"],
                "text/csv": [".csv"],
                "application/json": [".json"],
            },
            on_drop=UploadState.handle_upload(rx.upload_files(upload_id="doc_upload")),
        ),
        rx.cond(
            UploadState.upload_error != "",
            rx.text(
                UploadState.upload_error,
                color=tokens.COLOR["error"],
                size="2",
                margin_top="6px",
            ),
        ),
        rx.cond(
            DashboardState.docs.length() == 0,
            rx.text("No documents yet.", color=tokens.COLOR["text_muted"], margin_top="12px"),
            rx.vstack(
                rx.foreach(
                    DashboardState.docs,
                    lambda doc: rx.hstack(
                        rx.text(doc["filename"], size="2"),
                        rx.spacer(),
                        _status_pill(doc["status"]),
                        rx.cond(
                            doc["status"] == "error",
                            rx.button(
                                "Retry",
                                size="1",
                                on_click=UploadState.retry_document(doc["id"]),
                            ),
                        ),
                        rx.button(
                            "Delete",
                            size="1",
                            variant="outline",
                            on_click=DashboardState.delete_document(doc["id"]),
                        ),
                        width="100%",
                        padding_y="8px",
                        border_bottom=f"1px solid {tokens.COLOR['border']}",
                        align="center",
                    ),
                ),
                width="100%",
                margin_top="12px",
            ),
        ),
    )


def _search_card() -> rx.Component:
    return _card(
        rx.heading("Search your documents", size="4"),
        rx.text(
            "Find relevant passages from your uploaded reference documents.",
            color=tokens.COLOR["text_muted"],
        ),
        rx.hstack(
            rx.input(
                placeholder="e.g. What projects have I worked on?",
                value=DashboardState.search_query,
                on_change=DashboardState.set_search_query,
                width="100%",
            ),
            rx.button(
                rx.cond(DashboardState.searching, "Searching…", "Search"),
                on_click=DashboardState.search_documents,
                disabled=DashboardState.searching,
                flex_shrink="0",
            ),
            width="100%",
            margin_top="10px",
        ),
        rx.cond(
            DashboardState.search_error != "",
            rx.text(
                DashboardState.search_error,
                color=tokens.COLOR["error"],
                size="2",
                margin_top="8px",
            ),
        ),
        rx.cond(
            DashboardState.search_results.length() > 0,
            rx.vstack(
                rx.foreach(
                    DashboardState.search_results,
                    lambda passage: rx.box(
                        passage,
                        background=tokens.COLOR["accent_soft"],
                        border=f"1px solid {tokens.COLOR['border']}",
                        border_radius=tokens.RADIUS["sm"],
                        padding="10px 12px",
                        font_size="13px",
                        line_height="1.5",
                        white_space="pre-wrap",
                        width="100%",
                    ),
                ),
                width="100%",
                margin_top="12px",
                spacing="2",
            ),
            rx.cond(
                DashboardState.searching,
                rx.fragment(),
                rx.cond(
                    DashboardState.search_query != "",
                    rx.text(
                        "No relevant passages found.",
                        color=tokens.COLOR["text_muted"],
                        margin_top="12px",
                    ),
                    rx.fragment(),
                ),
            ),
        ),
    )


def _preferences_card() -> rx.Component:
    return _card(
        rx.heading("Preferences", size="4"),
        rx.text(
            f"How should {tokens.BRAND_NAME} answer you?",
            color=tokens.COLOR["text_muted"],
        ),
        rx.form(
            rx.text_area(
                name="preferences",
                default_value=DashboardState.preferences,
                rows="3",
                width="100%",
                placeholder="e.g. Answer coding questions in Python. Keep explanations concise.",
            ),
            rx.button(
                "Save preferences",
                type="submit",
                margin_top="8px",
                border_radius=tokens.RADIUS["pill"],
            ),
            on_submit=DashboardState.save_preferences,
        ),
        rx.cond(
            DashboardState.persona != "",
            rx.text(
                f"What {tokens.BRAND_NAME} knows about you: ",
                DashboardState.persona,
                color=tokens.COLOR["text_muted"],
                margin_top="12px",
            ),
        ),
    )


def _dashboard_header() -> rx.Component:
    return rx.hstack(
        rx.heading("Dashboard", size="6"),
        rx.spacer(),
        rx.cond(
            DashboardState.email != "",
            rx.text(DashboardState.email, color=tokens.COLOR["text_muted"], size="2"),
        ),
        rx.button("Sign out", on_click=DashboardState.sign_out, variant="outline"),
        width="100%",
        align="center",
        margin_bottom="18px",
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        nav(),
        rx.box(
            _dashboard_header(),
            onboarding_checklist(),
            _open_app_card(),
            _key_and_credits_card(),
            _trial_card(),
            _documents_card(),
            _search_card(),
            _preferences_card(),
            max_width="1040px",
            margin="0 auto",
            padding="24px",
        ),
        background=tokens.COLOR["bg"],
        min_height="100vh",
        on_mount=DashboardState.load_dashboard,
    )
