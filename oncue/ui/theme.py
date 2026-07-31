"""Shared theme for OnCUE desktop UI (overlay HUD + settings dialogs)."""

from __future__ import annotations

# Refined dark palette — readable on any wallpaper, aligned with marketing emerald accent.
COLOR = {
    "bg": "#09090f",
    "surface": "#12121a",
    "surface_raised": "#1a1a26",
    "surface_overlay": "rgba(18, 18, 28, 0.94)",
    "accent": "#34d399",
    "accent_soft": "rgba(52, 211, 153, 0.14)",
    "accent_border": "rgba(52, 211, 153, 0.45)",
    "accent_glow": "rgba(52, 211, 153, 0.22)",
    "text": "#f4f4f5",
    "text_muted_faint": "rgba(244, 244, 245, 0.45)",
    "text_muted": "rgba(244, 244, 245, 0.62)",
    "text_muted_strong": "rgba(244, 244, 245, 0.82)",
    "status_green": "#6ee7b7",
    "question_accent": "#a5b4fc",
    "confirm_yellow": "#fcd34d",
    "danger": "#f87171",
    "allow_border": "#34d399",
    "deny_border": "#f87171",
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "input_bg": "rgba(255, 255, 255, 0.05)",
    "input_border": "rgba(255, 255, 255, 0.12)",
    "input_focus_border": "rgba(52, 211, 153, 0.65)",
    "button_bg": "rgba(255, 255, 255, 0.06)",
    "button_bg_hover": "rgba(255, 255, 255, 0.1)",
    "button_border": "rgba(255, 255, 255, 0.14)",
    "button_primary_bg": "#059669",
    "button_primary_hover": "#10b981",
    "inline_code_bg": "rgba(255, 255, 255, 0.08)",
    "code_block_bg": "#0c0c14",
    "code_block_text": "#d1fae5",
    "code_block_border": "rgba(52, 211, 153, 0.25)",
    "answer_border": "rgba(255, 255, 255, 0.06)",
    # Legacy aliases used by overlay
    "panel_bg": "rgba(18, 18, 28, 0.94)",
    "question_purple": "#a5b4fc",
}

FONT = {
    "family": "'Inter', 'Segoe UI', system-ui, sans-serif",
    "mono": "'JetBrains Mono', 'Cascadia Code', Consolas, monospace",
}

RADIUS = {"panel": "14px", "pill": "999px", "control": "8px", "code": "10px"}

HOTKEY_CHIP_STYLE = f"""
    background: {COLOR['surface_raised']};
    border: 1px solid {COLOR['border_subtle']};
    border-radius: 6px;
    padding: 5px 10px;
    font-family: {FONT['mono']};
    font-size: 11px;
    color: {COLOR['accent']};
"""

MUTED_CARD_STYLE = f"""
    background: {COLOR['surface_raised']};
    border: 1px solid {COLOR['border_subtle']};
    border-radius: {RADIUS['panel']};
    padding: 12px 14px;
"""

SCROLL_STYLE = f"""
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {COLOR['border_subtle']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR['accent_border']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background: {COLOR['bg']};
    color: {COLOR['text']};
}}
QGroupBox {{
    background: {COLOR['surface']};
    border: 1px solid {COLOR['border_subtle']};
    border-radius: {RADIUS['panel']};
    margin-top: 18px;
    padding: 16px 14px 12px;
    font-size: 12px;
    font-weight: 600;
    color: {COLOR['text_muted_strong']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {COLOR['accent']};
}}
QLabel {{
    color: {COLOR['text_muted_strong']};
    font-size: 12px;
}}
QLineEdit {{
    background: {COLOR['input_bg']};
    border: 1px solid {COLOR['input_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 8px 10px;
    font-size: 13px;
    selection-background-color: {COLOR['accent_soft']};
}}
QLineEdit:focus {{
    border: 1px solid {COLOR['input_focus_border']};
    background: rgba(255, 255, 255, 0.07);
}}
QComboBox {{
    background: {COLOR['input_bg']};
    border: 1px solid {COLOR['input_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 6px 10px;
    font-size: 13px;
    min-height: 22px;
}}
QComboBox:focus {{
    border: 1px solid {COLOR['input_focus_border']};
}}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {COLOR['text_muted']};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {COLOR['surface_raised']};
    border: 1px solid {COLOR['border_subtle']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    selection-background-color: {COLOR['accent_soft']};
    selection-color: {COLOR['text']};
    padding: 4px;
    outline: none;
}}
QCheckBox {{
    color: {COLOR['text_muted_strong']};
    font-size: 12px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {COLOR['input_border']};
    border-radius: 4px;
    background: {COLOR['input_bg']};
}}
QCheckBox::indicator:checked {{
    background: {COLOR['accent']};
    border-color: {COLOR['accent']};
}}
QPushButton {{
    background: {COLOR['button_bg']};
    border: 1px solid {COLOR['button_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {COLOR['button_bg_hover']};
    border-color: {COLOR['accent_border']};
}}
QPushButton#primary {{
    background: {COLOR['button_primary_bg']};
    border: 1px solid {COLOR['accent']};
    color: #ecfdf5;
    font-weight: 600;
}}
QPushButton#primary:hover {{
    background: {COLOR['button_primary_hover']};
}}
QDialogButtonBox QPushButton {{
    padding: 8px 20px;
    min-width: 80px;
}}
"""

HEADER_TITLE_STYLE = (
    f"font-size: 20px; font-weight: 700; color: {COLOR['text']}; letter-spacing: -0.02em;"
)
HEADER_SUBTITLE_STYLE = f"font-size: 12px; color: {COLOR['text_muted']};"
BRAND_DOT_STYLE = (
    f"font-size: 14px; font-weight: 700; color: {COLOR['accent']};"
)
