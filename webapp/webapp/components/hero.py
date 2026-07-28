import reflex as rx

from webapp.styles import tokens

# Copy is reused verbatim from the copy-reviewed GTM deck
# (.claude/campaigns/parakeet-launch/landing-page.md, "Hero" section) —
# never invent new marketing copy here. The overlay-privacy framing is
# strictly "stays private during your own demos/calls" per
# .claude/campaigns/parakeet-launch/positioning.md's standing guardrail —
# never interview/exam-evasion language.


def hero() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Speak Hinglish. Ask your screen. Skip the alt-tab entirely.",
            size="9", text_align="center", max_width="680px",
            font_family=tokens.FONT["sans"],
        ),
        rx.text(
            "Hold one key and dictate in Hinglish straight into WhatsApp, ChatGPT, "
            "or any text box. Press another and get an instant answer about whatever's "
            "on your screen — no typing, no translating your thoughts into English first.",
            color=tokens.COLOR["text_muted"], text_align="center",
            max_width="520px", size="4",
        ),
        rx.hstack(
            rx.link(
                "Get started free", href="/login",
                background=tokens.COLOR["accent"], color="white",
                padding="12px 22px", border_radius=tokens.RADIUS["pill"],
                text_decoration="none", font_weight="600",
            ),
            rx.link(
                "See how it works", href="#how-it-works",
                color=tokens.COLOR["text"], padding="12px 4px",
                text_decoration="underline",
            ),
            spacing="4", margin_top="8px",
        ),
        rx.text(
            "No API key needed — hosted access starts the moment you sign up.",
            color=tokens.COLOR["text_muted"], size="2",
        ),
        # No demo video exists yet (webapp/webapp/assets/ is a placeholder) —
        # don't reference a broken asset; this box is a stand-in until a real
        # demo is recorded, matching the "no fabricated content" rule already
        # applied to social_proof.py.
        rx.box(
            rx.center(
                rx.text(
                    "Demo video coming soon",
                    color=tokens.COLOR["text_muted"], size="3",
                ),
                height="360px",
            ),
            background=tokens.COLOR["surface"],
            border=f"1px solid {tokens.COLOR['border']}",
            border_radius=tokens.RADIUS["md"],
            box_shadow=tokens.SHADOW_CARD,
            padding="10px", max_width="720px", width="100%", margin_top="32px",
        ),
        spacing="5", align="center", padding="64px 24px 32px",
    )
