#!/usr/bin/env python3
"""Walk through every OnCUE Settings section + feature guide (screen recording)."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
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


def _callout(title: str, detail: str) -> QWidget:
    w = QWidget()
    w.setWindowTitle("OnCUE tour")
    w.setStyleSheet(
        "background:#0f172a;color:#e2e8f0;font-size:13px;padding:14px;"
        "border:2px solid #78c878;border-radius:8px;"
    )
    lay = QVBoxLayout(w)
    t = QLabel(f"<b>{title}</b>")
    t.setTextFormat(Qt.TextFormat.RichText)
    lay.addWidget(t)
    d = QLabel(detail)
    d.setWordWrap(True)
    lay.addWidget(d)
    _center(w, 540, 130)
    return w


def _load_env_test() -> dict[str, str]:
    path = Path(__file__).resolve().parents[1] / ".env.test"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _apply_test_hosted(env: dict[str, str]) -> None:
    if not env.get("ONCUE_TOKEN"):
        return
    from urllib.parse import urlencode

    from oncue.config import Config, set_config
    from oncue.protocol import apply_url

    web = env.get("ONCUE_WEB_URL", "http://localhost:3001")
    rag = env.get("ONCUE_RAG_URL", f"{web}/mock/rag")
    backend = env.get("ONCUE_BACKEND_URL", "http://localhost:4000/v1")
    token = env["ONCUE_TOKEN"]
    apply_url(
        f"oncue://connect?{urlencode({'token': token, 'web': web, 'rag': rag, 'backend': backend})}"
    )
    set_config(
        Config(
            provider="hosted",
            oncue_token=token,
            web_url=web,
            rag_url=rag,
            backend_url=backend,
            hosted_model=env.get("HOSTED_MODEL", "oncue-default"),
        )
    )


# (section_key, banner_title, banner_detail, dwell_ms)
_TOUR_STEPS: list[tuple[str, str, str, int]] = [
    (
        "quick_start",
        "Quick start",
        "Parakeet-style: web login → Open OnCUE app. Clicky-style: hotkey cheat sheet "
        "so you never Alt-Tab to ChatGPT.",
        2800,
    ),
    (
        "provider",
        "AI provider",
        "Pick hosted (license key) or BYO: groq (free dev), claude, gpt, gemini.",
        2400,
    ),
    (
        "api_keys",
        "API keys",
        "Bring-your-own keys. Groq is free at console.groq.com. Tavily enables web search.",
        2600,
    ),
    (
        "hosted",
        "OnCUE hosted",
        "Backend + website + RAG URLs and license key. Trial status shows live from dashboard.",
        2800,
    ),
    (
        "speech",
        "Speech",
        "Hinglish dictation, Groq cloud STT (fast) vs local Whisper (offline/private).",
        2600,
    ),
    (
        "behavior",
        "Behavior",
        "All 5 hotkeys, allowed folders, screen-share hiding (Parakeet privacy), "
        "system actions + confirm prompts.",
        3000,
    ),
]


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("OnCUE Settings Tour")

    env = _load_env_test()
    _apply_test_hosted(env)

    from oncue.ui.feature_guide import FeatureGuideDialog
    from oncue.ui.onboarding import OnboardingDialog
    from oncue.ui.settings import SettingsDialog

    settings = SettingsDialog()
    _center(settings, 560, 620)
    settings.show()

    state = {"step": 0, "callout": None, "guide": None}

    def run_step() -> None:
        if state["callout"]:
            state["callout"].close()
            state["callout"] = None

        i = state["step"]
        if i >= len(_TOUR_STEPS):
            settings.close()
            onboard = OnboardingDialog()
            _center(onboard, 500, 400)
            onboard.show()
            QTimer.singleShot(2800, app.quit)
            return

        key, title, detail, dwell = _TOUR_STEPS[i]
        settings.scroll_to_section(key)
        settings.raise_()
        c = _callout(title, detail)
        c.show()
        state["callout"] = c
        state["step"] = i + 1
        QTimer.singleShot(dwell, run_step)

    def start_tour() -> None:
        if state["guide"]:
            state["guide"].close()
        QTimer.singleShot(400, run_step)

    guide = FeatureGuideDialog()
    _center(guide, 540, 500)
    guide.show()
    state["guide"] = guide
    QTimer.singleShot(3500, start_tour)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
