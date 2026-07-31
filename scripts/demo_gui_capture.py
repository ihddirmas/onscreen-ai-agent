#!/usr/bin/env python3
"""OnCUE desktop UI walkthrough for screen capture (isolated X display)."""
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
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

    # 1) Overlay with streamed answer
    overlay = Overlay()
    overlay.set_trial_status(1)
    _center(overlay, 520, 380)
    overlay.show_for_input()
    overlay.show_question("what's this TypeError on line 42?")
    overlay.begin_answer("Thinking…")
    for chunk in (
        "The **TypeError** means a string was passed where a number is expected.\n\n"
        "- Use `Number(value)` at the call site\n"
        "- Check `processCount` in utils.ts line 42"
    ):
        for ch in chunk:
            overlay.append_token(ch)
            app.processEvents()
    overlay.finish()
    app.processEvents()
    input("OVERLAY")  # noqa: T201 — pause marker for ffmpeg segment timing

    overlay.hide()

    # 2) Settings
    settings = SettingsDialog()
    _center(settings, 560, 640)
    settings.show()
    app.processEvents()
    input("SETTINGS")

    settings.close()

    # 3) Onboarding
    onboard = OnboardingDialog()
    _center(onboard, 500, 360)
    onboard.setWindowModality(Qt.WindowModality.ApplicationModal)
    onboard.show()
    app.processEvents()
    input("ONBOARDING")

    onboard.close()


if __name__ == "__main__":
    main()
