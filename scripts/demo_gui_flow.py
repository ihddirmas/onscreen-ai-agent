#!/usr/bin/env python3
"""Walk through OnCUE desktop UI for screen recordings (no network/audio needed)."""
from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


def _center(widget, w: int, h: int) -> None:
    widget.resize(w, h)
    geo = widget.frameGeometry()
    screen = QApplication.primaryScreen()
    if screen:
        center = screen.availableGeometry().center()
        geo.moveCenter(center)
        widget.move(geo.topLeft())
    widget.raise_()
    widget.activateWindow()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("OnCUE")

    from oncue.ui.onboarding import OnboardingDialog
    from oncue.ui.overlay import Overlay
    from oncue.ui.settings import SettingsDialog

    overlay = Overlay()
    overlay.set_trial_status(1)
    overlay.show_for_input()
    overlay.show_question("what's this TypeError on line 42?")
    overlay.begin_answer("Thinking…")

    answer = (
        "The **TypeError** means you're passing a string where a number is expected.\n\n"
        "- Wrap with `Number(value)` at the call site\n"
        "- Or validate input before the function runs\n\n"
        "The stack trace points to `processCount` in `utils.ts`."
    )
    idx = {"i": 0}

    def stream_tokens() -> None:
        i = idx["i"]
        if i < len(answer):
            overlay.append_token(answer[i])
            idx["i"] = i + 1
            QTimer.singleShot(25, stream_tokens)
        else:
            overlay.finish()
            QTimer.singleShot(2200, show_settings)

    settings_dialog: list[SettingsDialog] = []

    def show_settings() -> None:
        overlay.hide()
        dialog = SettingsDialog()
        settings_dialog.append(dialog)
        _center(dialog, 560, 640)
        dialog.show()
        QTimer.singleShot(2800, show_onboarding)

    def show_onboarding() -> None:
        if settings_dialog:
            settings_dialog[0].close()
        onboard = OnboardingDialog()
        _center(onboard, 500, 380)
        onboard.show()
        QTimer.singleShot(2800, app.quit)

    QTimer.singleShot(800, stream_tokens)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
