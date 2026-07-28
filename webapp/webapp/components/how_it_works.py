import reflex as rx

from webapp.styles import tokens

# Steps mirror .claude/campaigns/parakeet-launch/landing-page.md's
# "How it works" + "Solution" sections — real, shipped hotkeys, not
# aspirational copy.
_STEPS = [
    (
        "1",
        "Press or hold your hotkey",
        "Ctrl+Shift+Space to ask about your screen, Ctrl+Shift+D to dictate, "
        "Ctrl+Shift+M during any call.",
    ),
    (
        "2",
        "Parakeet captures exactly what it needs",
        "A screenshot, your voice, or your voice plus the call audio — whichever "
        "the hotkey calls for.",
    ),
    (
        "3",
        "The answer streams onto the overlay",
        "A floating, transparent window — or the text types straight into "
        "whatever box you clicked into. Invisible in screen shares and "
        "recordings by default, so it stays private during your own demos or calls.",
    ),
]


def how_it_works() -> rx.Component:
    return rx.vstack(
        rx.heading("How it works", size="6", text_align="center"),
        rx.hstack(
            *[
                rx.vstack(
                    rx.text(num, size="6", weight="bold", color=tokens.COLOR["text_muted"]),
                    rx.text(title, weight="bold", size="4"),
                    rx.text(body, color=tokens.COLOR["text_muted"], size="2", text_align="center"),
                    max_width="240px", align="center", spacing="2",
                )
                for num, title, body in _STEPS
            ],
            spacing="7", justify="center", flex_wrap="wrap", margin_top="24px",
        ),
        id="how-it-works", padding="48px 24px", max_width="1040px", margin="0 auto",
    )
