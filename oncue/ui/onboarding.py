"""First-run onboarding: point new users at the free hosted trial (no API key
setup) instead of silently defaulting to an unconfigured BYOK provider. Shown
once — either choice dismisses it for good.
"""

from __future__ import annotations

import webbrowser

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from oncue.config import get_config
from oncue.ui.theme import COLOR, DIALOG_STYLE


class OnboardingDialog(QDialog):
    """First-launch choice: free hosted trial (no key needed) vs. bring your
    own provider key. Emits `open_settings` if the user picks the BYOK path."""

    open_settings = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to OnCUE")
        self.setMinimumWidth(480)
        self.setStyleSheet(DIALOG_STYLE)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("How do you want to get started?")
        title.setStyleSheet(
            f"font-size: 17px; font-weight: 600; color: {COLOR['text']};"
        )
        root.addWidget(title)

        body = QLabel(
            "Sign in for a free hosted trial — screenshot Q&A, Hinglish dictation, "
            "and document-grounded answers with no API keys.\n\n"
            "Or bring your own Groq / Claude / GPT / Gemini key if you prefer."
        )
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {COLOR['text_muted_strong']}; line-height: 1.5;")
        root.addWidget(body)

        tips = QLabel(
            "Hotkeys (customizable in Settings):\n"
            "  Ctrl+Shift+Space — ask about your screen\n"
            "  Ctrl+Shift+D — dictate at cursor (hold)\n"
            "  Ctrl+Shift+H — chat without screenshot"
        )
        tips.setStyleSheet(
            f"color: {COLOR['text_muted']}; font-size: 11px;"
        )
        tips.setWordWrap(True)
        root.addWidget(tips)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {COLOR['confirm_yellow']};")
        self._status.hide()
        root.addWidget(self._status)

        buttons = QHBoxLayout()
        self._trial_btn = QPushButton("Sign in for free hosted trial")
        self._trial_btn.clicked.connect(self._start_trial)
        key_btn = QPushButton("I have my own API key")
        key_btn.clicked.connect(self._use_own_key)
        buttons.addWidget(self._trial_btn)
        buttons.addWidget(key_btn)
        root.addLayout(buttons)

    def _start_trial(self) -> None:
        cfg = get_config()
        if not cfg.web_url:
            self._status.setText(
                "This build doesn't have a website URL configured yet. "
                "Use your own API key below, or set ONCUE_WEB_URL in the environment."
            )
            self._status.show()
            return
        webbrowser.open(f"{cfg.web_url.rstrip('/')}/login")
        self.accept()

    def _use_own_key(self) -> None:
        self.open_settings.emit()
        self.accept()
