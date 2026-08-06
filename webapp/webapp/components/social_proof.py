import reflex as rx

from webapp.styles import tokens

# Honest use-case framing, not fabricated reviews or invented names — see
# .claude/campaigns/oncue-launch/landing-page.md "Social proof" section:
# no real testimonials exist yet, so this stays a "Built for" row of
# concrete, verifiable use cases rather than star ratings or quotes
# attributed to a specific named person. Swap for real, permissioned
# testimonials once collected.
_USE_CASES = [
    ("🎓", "Students", "Screenshot a doubt mid-lecture and ask about it in Hinglish — "
                        "no need to translate the question into English first."),
    ("💻", "Developers", "Reading an unfamiliar codebase, screenshot a function and ask "
                          "what it does instead of tracing call sites by hand."),
    ("📞", "On calls", "Look something up mid-call — a client demo, a team standup, "
                        "a lecture — without going silent. The overlay stays private "
                        "during your own screen share."),
]


def _card(icon: str, who: str, quote: str) -> rx.Component:
    return rx.box(
        rx.text(icon, size="6"),
        rx.text(who, weight="bold", size="3", margin_top="10px", margin_bottom="6px"),
        rx.text(quote, color=tokens.COLOR["text_muted"], size="2"),
        background=tokens.COLOR["surface"],
        border=f"1px solid {tokens.COLOR['border']}",
        border_radius=tokens.RADIUS["md"],
        box_shadow=tokens.SHADOW_CARD,
        padding="22px", max_width="280px",
        transition="transform 0.15s ease, box-shadow 0.15s ease",
        _hover={"transform": "translateY(-4px)", "box_shadow": tokens.SHADOW_FLOAT},
    )


def social_proof() -> rx.Component:
    return rx.vstack(
        rx.badge("BUILT FOR", color_scheme="iris", variant="soft", radius="full", size="2"),
        rx.heading(
            "Real use cases, not stock testimonials", size="6", text_align="center",
            font_family=tokens.FONT["serif"], margin_top="10px",
        ),
        rx.hstack(
            *[_card(icon, who, quote) for icon, who, quote in _USE_CASES],
            spacing="4", justify="center", flex_wrap="wrap", margin_top="24px",
        ),
        padding="56px 24px", max_width="1040px", margin="0 auto", align="center",
    )
