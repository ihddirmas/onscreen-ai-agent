import reflex as rx

from webapp.components.overlay_mockup import overlay_mockup
from webapp.styles import tokens

# Steps mirror .claude/campaigns/parakeet-launch/landing-page.md's
# "How it works" + "Solution" sections — real, shipped hotkeys, not
# aspirational copy. Each step now renders as its own full-bleed color band
# (mymind.com's structural pattern for depth/rhythm) with a mockup of what
# that step actually looks like, alternating text/mockup sides.
_STEPS = [
    (
        "PRESS",
        "mint",
        "Press or hold your hotkey",
        "Ctrl+Shift+Space to ask about your screen, Ctrl+Shift+D to dictate, "
        "Ctrl+Shift+M during any call.",
        "what's on my screen?",
        "Got it — that's a merge conflict in App.tsx. Keep the incoming branch's "
        "import order, then re-run the build.",
    ),
    (
        "CAPTURE",
        "violet",
        "OnCUE captures exactly what it needs",
        "A screenshot, your voice, or your voice plus the call audio — whichever "
        "the hotkey calls for.",
        "kal ka weather check karo",
        "Kal Delhi mein 34°C tak jaayega, thoda humid rahega — chhata saath "
        "rakhna better hoga.",
    ),
    (
        "STREAM",
        "dark",
        "The answer streams onto the overlay",
        "A floating, transparent window — or the text types straight into "
        "whatever box you clicked into. Invisible in screen shares and "
        "recordings by default, so it stays private during your own demos or calls.",
        "summarize this thread",
        "Three asks: extend the deadline to Friday, confirm the budget line, "
        "and loop in design before the next sync.",
    ),
]

_TAG_STYLE = {
    "mint": {"bg": tokens.BAND["mint_tag_bg"], "text": tokens.BAND["mint_tag_text"]},
    "violet": {"bg": tokens.BAND["violet_tag_bg"], "text": tokens.BAND["violet_tag_text"]},
    "dark": {"bg": "rgba(255,255,255,0.1)", "text": tokens.BAND["dark_text"]},
}


def _band(num: int, tag: str, color: str, title: str, body: str, question: str, answer: str) -> rx.Component:
    is_dark = color == "dark"
    bg = tokens.BAND["dark_bg"] if is_dark else tokens.BAND[f"{color}_bg"]
    text_color = tokens.BAND["dark_text"] if is_dark else tokens.COLOR["text"]
    muted_color = tokens.BAND["dark_text_muted"] if is_dark else tokens.COLOR["text_muted"]
    tag_style = _TAG_STYLE[color]

    text_col = rx.vstack(
        rx.badge(
            f"STEP {num} · {tag}",
            style={"background": tag_style["bg"], "color": tag_style["text"]},
            radius="full", size="2",
        ),
        rx.heading(title, size="7", color=text_color, font_family=tokens.FONT["serif"], margin_top="14px"),
        rx.text(body, color=muted_color, size="3", margin_top="10px", max_width="380px"),
        align_items="start", spacing="1",
    )
    mockup_col = rx.box(overlay_mockup(question=question, answer=answer))

    # Alternate text/mockup sides per step for the editorial, grid-breaking
    # composition the design-quality guardrail asks for, rather than every
    # row reading identically.
    children = [text_col, mockup_col] if num % 2 == 1 else [mockup_col, text_col]

    return rx.box(
        rx.hstack(
            *children,
            spacing="8", align="center", justify="center",
            flex_wrap="wrap", max_width="1040px", margin="0 auto",
        ),
        background=bg,
        width="100%",
        padding="56px 24px",
    )


def how_it_works() -> rx.Component:
    return rx.box(
        rx.heading(
            "How it works", size="7", text_align="center",
            font_family=tokens.FONT["serif"], padding_top="48px", padding_bottom="8px",
        ),
        *[
            _band(i + 1, tag, color, title, body, q, a)
            for i, (tag, color, title, body, q, a) in enumerate(_STEPS)
        ],
        id="how-it-works",
    )
