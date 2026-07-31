"""First-run onboarding: hosted trial vs bring-your-own key."""

from __future__ import annotations

import webbrowser

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from oncue.config import get_config
from oncue.ui.theme import (
    BRAND_DOT_STYLE,
    COLOR,
    DIALOG_STYLE,
    HEADER_SUBTITLE_STYLE,
    HEADER_TITLE_STYLE,
    MUTED_CARD_STYLE,
)


class OnboardingDialog(QDialog):
    """First-launch choice: free hosted trial (no key needed) vs. bring your
    own provider key. Emits `open_settings` if the user picks the BYOK path."""

    open_settings = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to OnCUE")
        self.setMinimumWidth(500)
        self.setStyleSheet(DIALOG_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)

        header = QHBoxLayout()
        brand = QLabel("●")
        brand.setStyleSheet(BRAND_DOT_STYLE)
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title = QLabel("Welcome to OnCUE")
        title.setStyleSheet(HEADER_TITLE_STYLE)
        subtitle = QLabel("Your on-screen AI agent — screenshot, voice, and dictation")
        subtitle.setStyleSheet(HEADER_SUBTITLE_STYLE)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addWidget(brand)
        header.addLayout(title_col)
        root.addLayout(header)

        body = QLabel(
            "Start with a <b>free hosted trial</b> (no API keys) — screenshot Q&A, "
            "Hinglish dictation, and document-grounded answers.\n\n"
            "Or connect your own Groq / Claude / GPT / Gemini key."
        )
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setStyleSheet(f"color: {COLOR['text_muted_strong']}; font-size: 13px; line-height: 1.5;")
        root.addWidget(body)

        tips = QLabel(
            "Ctrl+Shift+Space · screen Q&A\n"
            "Ctrl+Shift+D · dictate (hold)\n"
            "Ctrl+Shift+H · chat without screenshot\n\n"
            "Tip: enable “Hide from screen sharing” in Settings for private Zoom/Meet."
        )
        tips.setWordWrap(True)
        tips.setStyleSheet(MUTED_CARD_STYLE + f" color: {COLOR['text_muted']}; font-size: 11px;")
        root.addWidget(tips)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {COLOR['confirm_yellow']}; font-size: 12px;")
        self._status.hide()
        root.addWidget(self._status)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self._trial_btn = QPushButton("Sign in — free hosted trial")
        self._trial_btn.setObjectName("primary")
        self._trial_btn.clicked.connect(self._start_trial)
        key_btn = QPushButton("I have an API key")
        key_btn.clicked.connect(self._use_own_key)
        buttons.addWidget(self._trial_btn, stretch=1)
        buttons.addWidget(key_btn, stretch=1)
        root.addLayout(buttons)

    def _start_trial(self) -> None:
        cfg = get_config()
        if not cfg.web_url:
            self._status.setText(
                "No website URL configured. Use your API key below, or set ONCUE_WEB_URL."
            )
            self._status.show()
            return
        webbrowser.open(f"{cfg.web_url.rstrip('/')}/login")
        self.accept()

    def _use_own_key(self) -> None:
        self.open_settings.emit()
        self.accept()
