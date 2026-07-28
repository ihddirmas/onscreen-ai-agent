import reflex as rx

from webapp.styles import tokens

# Honest use-case framing, not fabricated reviews or invented names — see
# .claude/campaigns/parakeet-launch/landing-page.md "Social proof" section:
# no real testimonials exist yet, so this stays a "Built for" row of
# concrete, verifiable use cases rather than star ratings or quotes
# attributed to a specific named person. Swap for real, permissioned
# testimonials once collected.
_USE_CASES = [
    ("Students", "Screenshot a doubt mid-lecture and ask about it in Hinglish — "
                 "no need to translate the question into English first."),
    ("Developers", "Reading an unfamiliar codebase, screenshot a function and ask "
                    "what it does instead of tracing call sites by hand."),
    ("On calls", "Look something up mid-call — a client demo, a team standup, "
                  "a lecture — without going silent. The overlay stays private "
                  "during your own screen share."),
]


def social_proof() -> rx.Component:
    return rx.vstack(
        rx.heading("Built for", size="6", text_align="center"),
        rx.hstack(
            *[
                rx.box(
                    rx.text(who, weight="bold", size="3", margin_bottom="8px"),
                    rx.text(quote, color=tokens.COLOR["text_muted"], size="2"),
                    background=tokens.COLOR["surface"],
                    border=f"1px solid {tokens.COLOR['border']}",
                    border_radius=tokens.RADIUS["md"],
                    padding="20px", max_width="280px",
                )
                for who, quote in _USE_CASES
            ],
            spacing="4", justify="center", flex_wrap="wrap",
        ),
        padding="24px", max_width="1040px", margin="0 auto",
    )
