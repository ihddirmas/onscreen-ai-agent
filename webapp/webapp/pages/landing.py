import reflex as rx

from webapp.components.hero import hero
from webapp.components.how_it_works import how_it_works
from webapp.components.nav import nav
from webapp.components.pricing import pricing
from webapp.components.social_proof import social_proof
from webapp.styles import tokens


def _footer() -> rx.Component:
    return rx.center(
        rx.text(
            f"© {tokens.BRAND_NAME}",
            color=tokens.COLOR["text_muted"], size="1",
        ),
        padding="24px", border_top=f"1px solid {tokens.COLOR['border']}",
        margin_top="24px",
    )


def landing_page() -> rx.Component:
    return rx.box(
        nav(),
        hero(),
        how_it_works(),
        social_proof(),
        pricing(),
        _footer(),
        background=tokens.COLOR["bg"], min_height="100vh",
    )
