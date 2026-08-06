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
    "panel_bg": "rgba(14, 14, 22, 160)",
    "accent_border": "rgba(120, 200, 120, 140)",
    "accent_glow": "rgba(120, 200, 120, 40)",
    "text": "#f0f0f0",
    "text_muted_faint": "rgba(255, 255, 255, 72)",
    "text_muted": "rgba(255, 255, 255, 130)",
    "text_muted_strong": "rgba(255, 255, 255, 155)",
    "status_green": "#8fd48f",
    "question_purple": "#c9c9e0",
    "confirm_yellow": "#ffd479",
    "allow_border": "#8fd48f",
    "deny_border": "#d48f8f",
    "input_bg": "rgba(255, 255, 255, 22)",
    "input_border": "rgba(255, 255, 255, 50)",
    "input_focus_border": "rgba(120, 200, 120, 180)",
    "button_bg": "rgba(255, 255, 255, 28)",
    "button_bg_hover": "rgba(255, 255, 255, 50)",
    "button_border": "rgba(255, 255, 255, 55)",
    "inline_code_bg": "rgba(255, 255, 255, 30)",
    "code_block_bg": "#0b0b12",
    "code_block_text": "#cde6cd",
    "code_block_border": "rgba(120, 200, 120, 60)",
    "answer_border": "rgba(255, 255, 255, 8)",
}

FONT = {
    "family": "Segoe UI",
    "mono": "Consolas,'Courier New',monospace",
}

RADIUS = {"panel": "12px", "pill": "16px", "control": "6px", "code": "8px"}
