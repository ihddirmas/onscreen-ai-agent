"""Full-screen transparent overlay that draws pointing arrows at screen
coordinates — the visual feedback when the model says "look here" via
[POINT:x,y] tags. Model coordinates are in image space (0-1280px wide,
from the downscaled screenshot) and are scaled up to native screen
resolution before rendering."""

from __future__ import annotations

import math
import re
import time

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

_ARROW_COLOR = QColor(80, 200, 255, 220)
_GLOW_COLOR = QColor(80, 200, 255, 60)

# How long a single point stays visible (seconds)
_POINT_DURATION = 4.0

# Regex to find [POINT:x,y] tags — works with optional spaces
_POINT_RE = re.compile(r"\[POINT\s*:\s*(\d+)\s*,?\s*(\d+)\s*\]")

# Image width that the model "sees" (matches capture.py MAX_WIDTH)
_MODEL_IMAGE_WIDTH = 1280


def model_to_screen(model_x: int, model_y: int) -> QPoint:
    """Scale model image coordinates to native screen coordinates."""
    virtual = QGuiApplication.primaryScreen().virtualGeometry()
    scale = virtual.width() / _MODEL_IMAGE_WIDTH
    return QPoint(int(model_x * scale), int(model_y * scale))


def parse_point_tags(text: str) -> list[QPoint]:
    """Extract all [POINT:x,y] tags from text and return screen coordinates."""
    points: list[QPoint] = []
    for m in _POINT_RE.finditer(text):
        img_x, img_y = int(m.group(1)), int(m.group(2))
        points.append(model_to_screen(img_x, img_y))
    return points


def strip_point_tags(text: str) -> str:
    """Remove [POINT:x,y] tags so they don't render in the answer text."""
    return _POINT_RE.sub("", text)


class PointingWidget(QWidget):
    """Transparent full-screen overlay that draws animated pointing arrows."""

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._points: list[tuple[QPoint, float]] = []  # (screen_pos, expire_at)

        # Glow fade timer — runs while any point is active
        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 fps
        self._timer.timeout.connect(self._tick)

        self._native_geometry = None

    def showEvent(self, event) -> None:
        """Resize to full virtual desktop on every show (in case monitors
        changed)."""
        self._resize_to_virtual()
        super().showEvent(event)

    def _resize_to_virtual(self) -> None:
        vg = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(vg)

    def point_at(self, screen_pos: QPoint) -> None:
        """Add a pointing arrow at the given screen coordinate."""
        self._points.append((screen_pos, time.monotonic() + _POINT_DURATION))
        if not self._timer.isActive():
            self._timer.start()
            self._resize_to_virtual()
            self.show()
            self.raise_()
        self.update()

    def clear_points(self) -> None:
        self._points.clear()
        self._timer.stop()
        self.hide()

    def _tick(self) -> None:
        now = time.monotonic()
        self._points = [(p, t) for p, t in self._points if t > now]
        if not self._points:
            self._timer.stop()
            self.hide()
            return
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        now = time.monotonic()

        for screen_pos, expire_at in self._points:
            remaining = max(0, expire_at - now)
            age_ratio = 1 - (remaining / _POINT_DURATION)  # 0 → 1

            # Fade out in the last 0.5s
            alpha = 1.0
            if age_ratio > 0.875:
                alpha = 1.0 - ((age_ratio - 0.875) / 0.125)

            # Bob slightly (subtle float-up animation)
            bob_offset = int(math.sin(age_ratio * math.pi * 4) * 6)

            x = screen_pos.x()
            y = screen_pos.y() + bob_offset

            # Glow ring
            glow_radius = 28
            glow = QColor(_GLOW_COLOR)
            glow.setAlpha(int(glow.alpha() * alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPoint(x, y), glow_radius, glow_radius)

            # Outer ring
            glow_outer = QColor(_GLOW_COLOR)
            glow_outer.setAlpha(int(glow_outer.alpha() * alpha * 0.4))
            painter.setBrush(glow_outer)
            painter.drawEllipse(QPoint(x, y), glow_radius + 14, glow_radius + 14)

            # Arrow head pointing down-right from the dot
            arrow_color = QColor(_ARROW_COLOR)
            arrow_color.setAlpha(int(arrow_color.alpha() * alpha))
            pen = QPen(arrow_color, 2.5)
            painter.setPen(pen)
            painter.setBrush(arrow_color)

            size = 10
            arrow = QPolygonF([
                QPoint(x + 4, y - size),
                QPoint(x + 4 + size, y + 4),
                QPoint(x - size + 4, y + 4),
            ])
            painter.drawPolygon(arrow)

            # Center dot
            painter.setPen(Qt.PenStyle.NoPen)
            center = QColor(255, 255, 255)
            center.setAlpha(int(center.alpha() * alpha))
            painter.setBrush(center)
            painter.drawEllipse(QPoint(x, y), 3, 3)
