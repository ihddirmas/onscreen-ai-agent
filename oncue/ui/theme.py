"""Shared theme constants for the desktop overlay UI (Overlay, DictationIndicator).

Dark/translucent HUD with monochrome silver-white accents — aligned with the
OnCUE marketing site (Instrument editorial palette).
"""

from __future__ import annotations

COLOR = {
    "panel_bg": "rgba(18, 18, 26, 230)",
    "accent_border": "rgba(255, 255, 255, 100)",
    "accent_glow": "rgba(255, 255, 255, 18)",
    "text": "#f0f0f0",
    "text_muted_faint": "rgba(255, 255, 255, 72)",
    "text_muted": "rgba(255, 255, 255, 130)",
    "text_muted_strong": "rgba(255, 255, 255, 155)",
    "status_accent": "#c8c8c8",
    "question_muted": "rgba(255, 255, 255, 175)",
    "confirm_yellow": "#ffd479",
    "allow_border": "#d4d4d4",
    "deny_border": "#c08080",
    "input_bg": "rgba(255, 255, 255, 18)",
    "input_border": "rgba(255, 255, 255, 45)",
    "input_focus_border": "rgba(255, 255, 255, 170)",
    "button_bg": "rgba(255, 255, 255, 24)",
    "button_bg_hover": "rgba(255, 255, 255, 46)",
    "button_border": "rgba(255, 255, 255, 50)",
    "inline_code_bg": "rgba(255, 255, 255, 28)",
    "code_block_bg": "#0b0b12",
    "code_block_text": "#e8e8e8",
    "code_block_border": "rgba(255, 255, 255, 40)",
    "answer_border": "rgba(255, 255, 255, 10)",
    "dialog_bg": "#12121a",
    "dialog_surface": "#1a1a26",
}

# Back-compat alias used in overlay stylesheets
COLOR["status_green"] = COLOR["status_accent"]
COLOR["question_purple"] = COLOR["question_muted"]

FONT = {
    "family": "Segoe UI",
    "mono": "Consolas,'Courier New',monospace",
}

RADIUS = {"panel": "12px", "pill": "16px", "control": "6px", "code": "8px"}

DIALOG_STYLESHEET = f"""
QDialog {{
    background: {COLOR['dialog_bg']};
    color: {COLOR['text']};
}}
QLabel {{
    color: {COLOR['text_muted_strong']};
    font-size: 13px;
}}
QLabel#title {{
    color: {COLOR['text']};
    font-size: 15px;
    font-weight: 600;
}}
QLabel#status {{
    color: {COLOR['confirm_yellow']};
}}
QPushButton {{
    background: {COLOR['button_bg']};
    border: 1px solid {COLOR['button_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 8px 16px;
    font-size: 13px;
}}
QPushButton:hover {{
    background: {COLOR['button_bg_hover']};
    border-color: {COLOR['accent_border']};
}}
QPushButton#primary {{
    background: {COLOR['text']};
    color: {COLOR['dialog_bg']};
    border-color: {COLOR['text']};
    font-weight: 600;
}}
QPushButton#primary:hover {{
    background: #e0e0e0;
}}
"""
