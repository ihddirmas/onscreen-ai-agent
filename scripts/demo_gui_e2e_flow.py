#!/usr/bin/env python3
"""Desktop GUI E2E walkthrough using real .env.test hosted credentials."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlencode

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


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


def _load_env_test() -> dict[str, str]:
    path = Path(__file__).resolve().parents[1] / ".env.test"
    if not path.exists():
        raise SystemExit("Missing .env.test — run: bash scripts/start_local_e2e_stack.sh")
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _status_banner(text: str) -> QWidget:
    w = QWidget()
    w.setWindowTitle("OnCUE E2E")
    w.setStyleSheet("background:#0f172a;color:#e2e8f0;font-size:14px;padding:12px;")
    lay = QVBoxLayout(w)
    label = QLabel(text)
    label.setWordWrap(True)
    lay.addWidget(label)
    _center(w, 520, 120)
    return w


def main() -> None:
    env = _load_env_test()
    token = env.get("ONCUE_TOKEN", "")
    web = env.get("ONCUE_WEB_URL", "http://localhost:3001")
    rag = env.get("ONCUE_RAG_URL", f"{web}/mock/rag")
    backend = env.get("ONCUE_BACKEND_URL", "http://localhost:4000/v1")

    app = QApplication(sys.argv)
    app.setApplicationName("OnCUE E2E")

    from oncue.protocol import apply_url
    from oncue.ui.onboarding import OnboardingDialog
    from oncue.ui.overlay import Overlay
    from oncue.ui.settings import SettingsDialog
    from oncue import usage
    from oncue.config import Config, set_config

    # Apply deep link (hosted connect flow)
    deep_link = f"oncue://connect?{urlencode({'token': token, 'web': web, 'rag': rag, 'backend': backend})}"
    apply_url(deep_link)

    cfg = Config(
        provider="hosted",
        oncue_token=token,
        web_url=web,
        rag_url=rag,
        backend_url=backend,
        hosted_model=env.get("HOSTED_MODEL", "oncue-default"),
    )
    set_config(cfg)

    trial = usage.check_session()
    trial_left = trial.get("trial_remaining", trial.get("session_count", 0))
    can_start = trial.get("can_start", True)

    banner = _status_banner(
        f"E2E test user connected\n"
        f"tier={trial.get('tier')} can_start={can_start} trial_remaining={trial_left}\n"
        f"web={web}"
    )
    banner.show()

    overlay = Overlay()
    overlay.set_trial_status(trial_left if isinstance(trial_left, int) else 1)
    overlay.show_for_input()
    overlay.show_question("E2E: explain this TypeError on line 42")
    overlay.begin_answer("Thinking…")

    answer = (
        "Connected to **hosted E2E** backend.\n\n"
        f"- Trial check: `can_start={can_start}`\n"
        f"- Usage API: `{web}/api/usage/check`\n\n"
        "The TypeError means a string was passed where a number is expected."
    )
    idx = {"i": 0}

    def stream_tokens() -> None:
        i = idx["i"]
        if i < len(answer):
            overlay.append_token(answer[i])
            idx["i"] = i + 1
            QTimer.singleShot(20, stream_tokens)
        else:
            overlay.finish()
            if can_start:
                usage.report_session_start()
            QTimer.singleShot(2000, show_blocked_or_settings)

    def show_blocked_or_settings() -> None:
        banner.close()
        recheck = usage.check_session()
        if not recheck.get("can_start", True):
            overlay.show_blocked("Trial session used", f"{web}/pricing")
            QTimer.singleShot(2500, show_settings)
        else:
            QTimer.singleShot(500, show_settings)

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
        QTimer.singleShot(2500, app.quit)

    QTimer.singleShot(1200, stream_tokens)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
