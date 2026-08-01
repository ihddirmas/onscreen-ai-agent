"""Shared theme constants for the desktop overlay UI (Overlay, DictationIndicator).

Deliberately dark/translucent — this is an always-on-top HUD over arbitrary
screen content, not a marketing surface, so it does NOT reuse webapp's
light-editorial tokens (webapp/webapp/styles/tokens.py). Accents are
monochrome silver/white to match the OnCUE marketing site (Instrument
editorial palette), not green brand chrome.
"""

from __future__ import annotations

COLOR = {
    "panel_bg": "rgba(14, 14, 22, 160)",
    "accent_border": "rgba(255, 255, 255, 110)",
    "accent_glow": "rgba(255, 255, 255, 22)",
    "text": "#f0f0f0",
    "text_muted_faint": "rgba(255, 255, 255, 72)",
    "text_muted": "rgba(255, 255, 255, 130)",
    "text_muted_strong": "rgba(255, 255, 255, 155)",
    "status_green": "#c8c8c8",
    "question_purple": "#c9c9e0",
    "confirm_yellow": "#ffd479",
    "allow_border": "#d4d4d4",
    "deny_border": "#d48f8f",
    "input_bg": "rgba(255, 255, 255, 22)",
    "input_border": "rgba(255, 255, 255, 50)",
    "input_focus_border": "rgba(255, 255, 255, 165)",
    "button_bg": "rgba(255, 255, 255, 28)",
    "button_bg_hover": "rgba(255, 255, 255, 50)",
    "button_border": "rgba(255, 255, 255, 55)",
    "inline_code_bg": "rgba(255, 255, 255, 30)",
    "code_block_bg": "#0b0b12",
    "code_block_text": "#e4e4e4",
    "code_block_border": "rgba(255, 255, 255, 45)",
    "answer_border": "rgba(255, 255, 255, 8)",
}

FONT = {
    "family": "Segoe UI",
    "mono": "Consolas,'Courier New',monospace",
}

RADIUS = {"panel": "12px", "pill": "16px", "control": "6px", "code": "8px"}
