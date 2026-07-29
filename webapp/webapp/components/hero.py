import reflex as rx

from webapp.components.overlay_mockup import overlay_mockup
from webapp.styles import tokens

# Copy is reused verbatim from the copy-reviewed GTM deck
# (.claude/campaigns/parakeet-launch/landing-page.md, "Hero" section) —
# never invent new marketing copy here. The overlay-privacy framing is
# strictly "stays private during your own demos/calls" per
# .claude/campaigns/parakeet-launch/positioning.md's standing guardrail —
# never interview/exam-evasion language.


def hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.badge(
                "ON-SCREEN AI COPILOT", color_scheme="grass", variant="soft",
                size="2", radius="full",
            ),
            rx.heading(
                "Speak Hinglish. Ask your screen. Skip the alt-tab entirely.",
                size="9", text_align="center", max_width="720px",
                font_family=tokens.FONT["serif"], line_height="1.1",
                margin_top="20px",
            ),
            rx.text(
                "Hold one key and dictate in Hinglish straight into WhatsApp, ChatGPT, "
                "or any text box. Press another and get an instant answer about whatever's "
                "on your screen — no typing, no translating your thoughts into English first.",
                color=tokens.COLOR["text_muted"], text_align="center",
                max_width="520px", size="4", margin_top="18px",
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
                spacing="4", margin_top="12px",
            ),
            rx.text(
                "No API key needed — hosted access starts the moment you sign up.",
                color=tokens.COLOR["text_muted"], size="2",
            ),
            # A real (if CSS-stylized) likeness of the actual overlay, not a
            # "demo video coming soon" placeholder or an unrelated stock
            # screenshot — no demo video exists yet, and this is more honest
            # than implying one does.
            rx.box(
                overlay_mockup(
                    question="what's on my screen?",
                    answer=(
                        "This is a React error boundary crash — the stack trace points "
                        "to a null ref in useEffect. Add a guard before accessing .current."
                    ),
                    width="440px",
                ),
                margin_top="40px",
                # Subtle scroll parallax — see the script in landing.py.
                # Negative factor: floats up slightly slower than the page
                # scrolls past it, the classic layered-depth parallax cue.
                custom_attrs={"data-parallax": "-0.06"},
            ),
            spacing="2", align="center", padding="72px 24px 56px",
            position="relative", z_index="1",
        ),
        background=tokens.HERO_GRADIENT,
        # Fixed attachment = the gradient stays put while the page scrolls
        # over it, a free zero-JS parallax layer (only visible while the
        # hero is still in view, same effect used on the JS-driven mockup
        # card below for the scrolled-past state).
        background_attachment="fixed",
        width="100%",
        style={"filter": "saturate(1.1)"},
    )
