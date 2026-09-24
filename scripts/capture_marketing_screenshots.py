#!/usr/bin/env python3
"""Capture real OnCUE Qt overlay screenshots for the marketing website.

Run: xvfb-run -a python scripts/capture_marketing_screenshots.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "public" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 960, 640


class MarketingScene(QWidget):
    """Fixed-size canvas: painted backdrop + embedded overlay widget."""

    def __init__(self, paint_backdrop):
        super().__init__()
        self._paint_backdrop = paint_backdrop
        self.setFixedSize(W, H)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        self._paint_backdrop(painter, self.rect())
        painter.end()


def _paint_vscode(p: QPainter, rect) -> None:
    p.fillRect(rect, QColor("#1e1e1e"))
    mono = QFont("Consolas", 10)
    p.setFont(mono)
    p.setPen(QColor("#f48771"))
    p.drawText(24, 48, "TypeError: Cannot read properties of undefined (reading 'profile')")
    p.setPen(QColor("#808080"))
    p.drawText(24, 68, "    at renderProfile (App.tsx:42:11)")
    p.setPen(QColor("#d4d4d4"))
    p.drawText(24, 100, "  40 |   return <span>{user.profile.name}</span>")
    p.setPen(QColor("#569cd6"))
    p.drawText(24, 116, "  41 | }")


def _paint_whatsapp(p: QPainter, rect) -> None:
    p.fillRect(rect, QColor("#0b141a"))
    p.setBrush(QColor("#005c4b"))
    p.setPen(Qt.PenStyle.NoPen)
    bubble = rect.adjusted(rect.width() // 3, rect.height() // 2, -24, -rect.height() // 2 + 40)
    p.drawRoundedRect(bubble, 8, 8)
    p.setPen(QColor("#e9edef"))
    p.setFont(QFont("Segoe UI", 11))
    p.drawText(bubble.adjusted(12, 8, -12, -8), Qt.AlignmentFlag.AlignLeft, "Type here…")


def _paint_chart(p: QPainter, rect) -> None:
    p.fillRect(rect, QColor("#fafafa"))
    p.setPen(QPen(QColor("#e5e5e5"), 1))
    inner = rect.adjusted(40, 40, -40, -80)
    p.drawRect(inner)
    bars = [0.4, 0.65, 0.55, 0.3, 0.48, 0.7, 0.62]
    bw = inner.width() // (len(bars) * 2)
    for i, h in enumerate(bars):
        x = inner.left() + i * (bw * 2) + bw // 2
        bh = int(inner.height() * h)
        p.fillRect(x, inner.bottom() - bh, bw, bh, QColor("#1a1a1a"))
    p.setPen(QColor("#737373"))
    p.setFont(QFont("Segoe UI", 11))
    p.drawText(40, 28, "Weekly signups")


def _paint_pdf(p: QPainter, rect) -> None:
    p.fillRect(rect, QColor("#f5f5f5"))
    page = rect.adjusted(80, 50, -80, -50)
    p.setBrush(QColor("#ffffff"))
    p.setPen(QPen(QColor("#d4d4d4"), 1))
    p.drawRect(page)
    p.setPen(QColor("#171717"))
    p.setFont(QFont("Georgia", 14))
    p.drawText(page.adjusted(20, 20, -20, -20), Qt.AlignmentFlag.AlignTop, "bio-chapter-7.pdf")
    p.setFont(QFont("Georgia", 10))
    p.setPen(QColor("#525252"))
    p.drawText(
        page.adjusted(20, 50, -20, -20),
        Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
        "The citric acid cycle begins when acetyl-CoA combines with oxaloacetate…",
    )


def _paint_zoom(p: QPainter, rect) -> None:
    p.fillRect(rect, QColor("#2d2d30"))
    p.setPen(QColor("#888888"))
    p.setFont(QFont("Segoe UI", 12))
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Zoom — Screen Share Active")
    slide = rect.adjusted(120, 80, -120, -120)
    p.setBrush(QColor("#ffffff"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(slide)
    p.setPen(QColor("#171717"))
    p.setFont(QFont("Segoe UI", 18))
    p.drawText(slide, Qt.AlignmentFlag.AlignCenter, "Q3 Pipeline Review")


def _setup_overlay(overlay, question: str, answer: str, *, chat: bool = False) -> None:
    overlay.set_trial_status(0)
    overlay.show_for_input(chat=chat)
    overlay.show_question(question)
    overlay.begin_answer("")
    overlay.append_token(answer)
    overlay.finish()
    overlay.input.hide()  # show answer-only for screenshot
    overlay.resize(400, min(overlay.sizeHint().height() + 40, 340))


def capture(app: QApplication, name: str, backdrop_fn, question: str, answer: str, **kwargs) -> None:
    scene = MarketingScene(backdrop_fn)
    from oncue.ui.overlay import Overlay

    overlay = Overlay(embedded=True, parent=scene, content_protection=False)
    _setup_overlay(overlay, question, answer, **kwargs)
    overlay.move(W - overlay.width() - 28, H - overlay.height() - 28)
    scene.show()
    app.processEvents()
    pixmap = scene.grab()
    path = OUT / f"{name}.png"
    pixmap.save(str(path))
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    scene.close()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("OnCUE")

    scenes = [
        (
            "use-case-debug",
            _paint_vscode,
            "why is this TypeError happening on line 42?",
            (
                "**user.profile** is undefined — the API returned null for guests.\n\n"
                "Add optional chaining: `user?.profile?.name`"
            ),
        ),
        (
            "use-case-dictate",
            _paint_whatsapp,
            "Ctrl+Shift+D — dictating…",
            "→ *Hinglish transcription lands in the focused field*",
        ),
        (
            "use-case-standup",
            _paint_chart,
            "summarize this chart for my standup",
            (
                "**Weekly signups dipped 18%** after Tuesday — mostly mobile onboarding.\n\n"
                "Suggest shortening the OTP step for India traffic."
            ),
        ),
        (
            "use-case-exam",
            _paint_pdf,
            "explain Krebs cycle from my notes",
            (
                "Per **bio-chapter-7.pdf**: the cycle oxidizes acetyl-CoA to CO₂, "
                "producing NADH and FADH₂ for the electron transport chain."
            ),
            {"chat": True},
        ),
        (
            "use-case-demo",
            _paint_zoom,
            "what should I say about Q3 pipeline?",
            (
                "Lead with the **enterprise pilot** — 3 logos in legal, $420k weighted pipeline. "
                "De-risk the timeline objection upfront."
            ),
        ),
        (
            "hero-standup",
            _paint_chart,
            "summarize this chart for my standup",
            (
                "**Weekly signups dipped 18%** after Tuesday.\n\n"
                "Completion at verify-phone fell from 72% → 51%. "
                "Suggest WhatsApp login for India cohort."
            ),
        ),
    ]

    for item in scenes:
        name, backdrop, question, answer = item[0], item[1], item[2], item[3]
        opts = item[4] if len(item) > 4 else {}
        capture(app, name, backdrop, question, answer, **opts)

    QTimer.singleShot(0, app.quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
