"""Shared theme constants for the desktop overlay UI (Overlay, DictationIndicator).

Deliberately dark/translucent — this is an always-on-top HUD over arbitrary
screen content, not a marketing surface, so it does NOT reuse webapp's
light-editorial tokens (webapp/webapp/styles/tokens.py). Dark/translucent/
minimal-chrome is both more legible over arbitrary backgrounds and consistent
with the screen-share-invisible positioning and competitor references
(Cluely, Wispr Flow). See Wave 1d of
.claude/plans/geminixprize-md-refineplan-md-modify-cu-transient-flamingo.md.

Every color here was previously duplicated independently in overlay.py and
indicator.py, which had already drifted apart (the panel border alpha was 90
in one file and 120 in the other for what's conceptually the same border) —
this module is the single source of truth going forward.
"""

from __future__ import annotations

COLOR = {
    # Lower alpha than a typical opaque panel — Windows now draws a real
    # OS-level acrylic blur-behind under this window (oncue/ui/blur.py),
    # so the QSS-drawn panel only needs enough tint to stay legible and
    # on-brand, not to hide the desktop. A near-opaque value here would sit
    # on top of the blur and cancel out the frosted-glass look entirely.
    "panel_bg": "rgba(18, 18, 24, 130)",
    # Shared accent border for every floating panel. 120 (the indicator's
    # previous value) was kept over the overlay's previous 90 — it reads more
    # clearly against busy/bright screen content.
    "accent_border": "rgba(120, 200, 120, 120)",
    "text": "#f0f0f0",
    "text_muted_faint": "rgba(255, 255, 255, 70)",  # resize hint
    "text_muted": "rgba(255, 255, 255, 120)",  # title bar hint
    # Checkbox label. Contrast against panel_bg (~rgb(18,18,24) at full
    # opacity) is ~4.6:1 — meets WCAG AA (4.5:1) for normal-size text.
    # Re-check this ratio if panel_bg or this alpha ever changes.
    "text_muted_strong": "rgba(255, 255, 255, 150)",
    "status_green": "#8fd48f",
    "question_purple": "#c9c9e0",
    "confirm_yellow": "#ffd479",
    "allow_border": "#8fd48f",
    "deny_border": "#d48f8f",
    "input_bg": "rgba(255, 255, 255, 18)",
    "input_border": "rgba(255, 255, 255, 40)",
    "button_bg": "rgba(255, 255, 255, 25)",
    "button_bg_hover": "rgba(255, 255, 255, 45)",
    "button_border": "rgba(255, 255, 255, 50)",
    "inline_code_bg": "rgba(255, 255, 255, 28)",
    "code_block_bg": "#0b0b12",
    "code_block_text": "#cde6cd",
}

FONT = {
    "family": "Segoe UI",
    "mono": "Consolas,'Courier New',monospace",
}

RADIUS = {"panel": "12px", "pill": "16px", "control": "6px", "code": "8px"}
