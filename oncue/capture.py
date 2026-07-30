"""Screen capture via mss, downscaled for token economy.

A full-res PNG screenshot costs ~6-7k vision tokens — more than Groq's free
8k tokens/minute budget once the agent loop resends it. Downscaling to
1280px-wide JPEG cuts that to ~1-2k tokens with no practical loss for
"what's on my screen" questions.
"""

from __future__ import annotations

import mss
import mss.tools

MAX_WIDTH = 1280
JPEG_QUALITY = 75


def screenshot_png(monitor: int = 1) -> bytes:
    """Grab a monitor (1 = primary), downscale, return JPEG bytes."""
    with mss.mss() as sct:
        if monitor >= len(sct.monitors):
            monitor = 1 if len(sct.monitors) > 1 else 0
        shot = sct.grab(sct.monitors[monitor])
        png = mss.tools.to_png(shot.rgb, shot.size)
    return _downscale(png)


def _downscale(png: bytes) -> bytes:
    from PySide6.QtCore import QBuffer
    from PySide6.QtGui import QImage

    img = QImage.fromData(png)
    if img.isNull():
        return png
    if img.width() > MAX_WIDTH:
        from PySide6.QtCore import Qt

        img = img.scaledToWidth(MAX_WIDTH, Qt.TransformationMode.SmoothTransformation)
    buf = QBuffer()
    buf.open(QBuffer.OpenModeFlag.WriteOnly)
    img.save(buf, "JPEG", JPEG_QUALITY)
    return bytes(buf.data())
