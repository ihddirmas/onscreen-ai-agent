"""A stylized rendering of the real desktop overlay (oncue/ui/theme.py's
actual colors, not stock art) — used as the "floating app mockup" in the
hero and how-it-works sections. Rendering the real UI, even approximated in
CSS, ties the marketing site to the actual product instead of a generic
placeholder or an unrelated stock screenshot."""
from __future__ import annotations

import reflex as rx

from webapp.styles import tokens


def overlay_mockup(
    question: str,
    answer: str,
    *,
    width: str = "360px",
) -> rx.Component:
    m = tokens.OVERLAY_MOCKUP
    return rx.box(
        rx.vstack(
            rx.text(
                f"🦜 {tokens.BRAND_NAME} — drag to move · Enter to ask · Esc to hide",
                color=m["text_muted"], size="1",
            ),
            rx.box(
                rx.text(f"🗨 {question}", color="#c9c9e0", size="2", font_style="italic"),
                border_left=f"2px solid {m['border']}",
                padding_left="8px",
            ),
            rx.text(answer, color=m["text"], size="2", line_height="1.5"),
            rx.box(
                rx.text("Ask a follow-up…", color=m["text_muted"], size="2"),
                background=m["input_bg"],
                border=f"1px solid {m['border']}",
                border_radius=tokens.RADIUS["sm"],
                padding="8px 10px",
                margin_top="4px",
            ),
            align_items="start",
            spacing="3",
            width="100%",
        ),
        background=m["panel_bg"],
        border=f"1px solid {m['border']}",
        border_radius=tokens.RADIUS["md"],
        box_shadow=tokens.SHADOW_FLOAT,
        padding="16px 18px",
        width=width,
        style={"backdropFilter": "blur(6px)"},
    )
