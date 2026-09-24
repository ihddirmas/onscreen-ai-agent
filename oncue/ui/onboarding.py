"""First-run onboarding: point new users at the free hosted trial (no API key
setup) instead of silently defaulting to an unconfigured BYOK provider. Shown
once — either choice dismisses it for good.
"""

from __future__ import annotations

import webbrowser

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from oncue.config import get_config
from oncue.ui.theme import DIALOG_STYLESHEET


class OnboardingDialog(QDialog):
    """First-launch choice: free hosted trial (no key needed) vs. bring your
    own provider key. Emits `open_settings` if the user picks the BYOK path."""

    open_settings = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to OnCUE")
        self.setMinimumWidth(440)
        self.setStyleSheet(DIALOG_STYLESHEET)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("How do you want to get started?", objectName="title")
        root.addWidget(title)

        body = QLabel(
            "Try it free for one session — no API key needed — "
            "or bring your own key from Groq, Claude, GPT, or Gemini if you'd "
            "rather manage that yourself."
        )
        body.setWordWrap(True)
        root.addWidget(body)

        self._status = QLabel("", objectName="status")
        self._status.setWordWrap(True)
        self._status.hide()
        root.addWidget(self._status)

        buttons = QHBoxLayout()
        self._trial_btn = QPushButton("Sign in for a free hosted trial", objectName="primary")
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
                "Use your own API key below for now."
            )
            self._status.show()
            return
        webbrowser.open(f"{cfg.web_url.rstrip('/')}/login")
        self.accept()

    def _use_own_key(self) -> None:
        self.open_settings.emit()
        self.accept()
