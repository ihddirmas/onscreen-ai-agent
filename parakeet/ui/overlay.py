"""Transparent always-on-top overlay: input line, status, streamed answer,
and the Allow/Deny confirmation prompt for gated actions."""

from __future__ import annotations

import html
import re

from PySide6.QtCore import QRect, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QGuiApplication, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizeGrip,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from parakeet.ui.pointer import strip_point_tags
from parakeet.ui.theme import COLOR, FONT, RADIUS

_CODE_STYLE = (
    f"background:{COLOR['code_block_bg']}; border:1px solid {COLOR['accent_border']}; "
    f"border-radius:{RADIUS['code']}; padding:8px; color:{COLOR['code_block_text']}; "
    f"white-space:pre-wrap; font-family:{FONT['mono']}; font-size:12px;"
)
_INLINE_STYLE = (
    f"background:{COLOR['inline_code_bg']}; border-radius:3px; padding:1px 4px; "
    f"font-family:{FONT['mono']};"
)


def _prose_to_html(text: str) -> str:
    """Escape prose, style inline `code`, keep line breaks."""
    out, last = [], 0
    for m in re.finditer(r"`([^`\n]+)`", text):
        out.append(html.escape(text[last:m.start()]))
        out.append(f'<code style="{_INLINE_STYLE}">{html.escape(m.group(1))}</code>')
        last = m.end()
    out.append(html.escape(text[last:]))
    return "".join(out).replace("\n", "<br>")


def markdown_to_html(text: str) -> str:
    """Render an answer: fenced ``` blocks become distinct code boxes,
    everything else is prose. Handles a still-open fence during streaming."""
    parts = text.split("```")
    chunks = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # inside a fenced code block
            code = part
            # drop a leading language tag line ("python\n...")
            if "\n" in code:
                first, rest = code.split("\n", 1)
                if first.strip() and " " not in first.strip() and len(first.strip()) < 20:
                    code = rest
            chunks.append(f'<pre style="{_CODE_STYLE}">{html.escape(code)}</pre>')
        elif part:
            chunks.append(f"<div>{_prose_to_html(part)}</div>")
    return "".join(chunks)


def _parse_geometry(s: str) -> QRect | None:
    try:
        x, y, w, h = (int(v) for v in s.split(","))
    except (ValueError, AttributeError):
        return None
    if w < 260 or h < 100:
        return None
    return QRect(x, y, w, h)

_STYLE = f"""
QFrame#panel {{
    background-color: {COLOR['panel_bg']};
    border: 1px solid {COLOR['accent_border']};
    border-radius: {RADIUS['panel']};
}}
QLineEdit {{
    background: {COLOR['input_bg']};
    border: 1px solid {COLOR['input_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 6px 8px;
    font-size: 13px;
}}
QLabel#status {{ color: {COLOR['status_green']}; font-size: 12px; }}
QLabel#question {{
    color: {COLOR['question_purple']}; font-size: 13px; font-style: italic;
    border-left: 2px solid {COLOR['accent_border']}; padding-left: 8px;
}}
QLabel#confirm {{ color: {COLOR['confirm_yellow']}; font-size: 13px; }}
QTextBrowser {{
    background: transparent;
    border: none;
    color: {COLOR['text']};
    font-size: 13px;
}}
QPushButton {{
    background: {COLOR['button_bg']};
    border: 1px solid {COLOR['button_border']};
    border-radius: {RADIUS['control']};
    color: {COLOR['text']};
    padding: 4px 14px;
}}
QPushButton:hover {{ background: {COLOR['button_bg_hover']}; }}
QPushButton#allow {{ border-color: {COLOR['allow_border']}; }}
QPushButton#deny  {{ border-color: {COLOR['deny_border']}; }}
QCheckBox {{ color: {COLOR['text_muted_strong']}; font-size: 10px; }}
QCheckBox::indicator {{ width: 12px; height: 12px; }}
"""


class Overlay(QWidget):
    submitted = Signal(str)         # user typed a question and hit Enter
    confirmed = Signal(bool)        # user answered the Allow/Deny prompt
    system_toggled = Signal(bool)   # System-actions checkbox flipped

    def __init__(
        self,
        click_through: bool = False,
        geometry: str = "",
        system_enabled: bool = True,
        content_protection: bool = True,
    ):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self._click_through = click_through
        self._drag_offset = None
        self._resize_edge = None       # "right" | "bottom" | "corner" while resizing
        self._resize_start = None      # (global pos, geometry) at resize start
        self._adjusting = False        # True during programmatic move/resize
        self._custom_geometry = False  # True once the user placed/sized it
        self._answer_buffer = ""       # raw streamed markdown, re-rendered per token
        self._answer_displayed = ""    # answer text with [POINT] tags stripped
        self._system_enabled = system_enabled
        self._content_protection = content_protection
        self.setMouseTracking(True)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(800)
        self._save_timer.timeout.connect(self._persist_geometry)
        self._build_ui()
        saved = _parse_geometry(geometry)
        if saved:
            self._custom_geometry = True
            self._adjusting = True
            self.setGeometry(saved)
            self._adjusting = False
        else:
            self._place()

    # --- layout ------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setStyleSheet(_STYLE)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        panel = QFrame(objectName="panel")
        panel.setMouseTracking(True)  # lets edge-hover cursor feedback reach us
        root.addWidget(panel)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        title = QLabel("OnCUE — drag to move · Enter to ask · Esc to hide")
        title.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
        lay.addWidget(title)

        self.input = QLineEdit(placeholderText="Ask about your screen…")
        self.input.returnPressed.connect(self._on_return)
        lay.addWidget(self.input)

        # the user's command (typed or spoken) — stays visible during the answer
        self.question = QLabel("", objectName="question")
        self.question.setWordWrap(True)
        self.question.hide()
        lay.addWidget(self.question)

        self.status = QLabel("", objectName="status")
        self.status.hide()
        lay.addWidget(self.status)

        self.answer = QTextBrowser()
        self.answer.setOpenExternalLinks(True)
        self.answer.setMinimumHeight(60)
        self.answer.hide()
        lay.addWidget(self.answer, stretch=1)

        # confirmation row (hidden until an action needs approval)
        self.confirm_label = QLabel("", objectName="confirm")
        self.confirm_label.setWordWrap(True)
        self.confirm_label.hide()
        lay.addWidget(self.confirm_label)

        self.confirm_row = QWidget()
        row = QHBoxLayout(self.confirm_row)
        row.setContentsMargins(0, 0, 0, 0)
        allow = QPushButton("Allow", objectName="allow")
        deny = QPushButton("Deny", objectName="deny")
        allow.clicked.connect(lambda: self._answer_confirm(True))
        deny.clicked.connect(lambda: self._answer_confirm(False))
        row.addStretch(1)
        row.addWidget(deny)
        row.addWidget(allow)
        self.confirm_row.hide()
        lay.addWidget(self.confirm_row)

        # bottom row: system-actions toggle · resize hint · grip
        grip_row = QHBoxLayout()
        grip_row.setContentsMargins(0, 0, 0, 0)
        self.system_checkbox = QCheckBox("System actions (apps · files · browser)")
        self.system_checkbox.setChecked(self._system_enabled)
        self.system_checkbox.setToolTip(
            "When off, OnCUE only answers — it can't open apps, files, or the "
            "browser, or read your local files."
        )
        self.system_checkbox.toggled.connect(self.system_toggled.emit)
        grip_row.addWidget(self.system_checkbox)
        grip_row.addStretch(1)
        hint = QLabel("◢ resize")
        hint.setStyleSheet(f"color: {COLOR['text_muted_faint']}; font-size: 10px;")
        grip_row.addWidget(hint)
        grip = QSizeGrip(panel)
        grip.setFixedSize(18, 18)
        grip_row.addWidget(grip)
        lay.addLayout(grip_row)

        self.setMinimumSize(280, 120)
        self.setFont(QFont(FONT["family"], 10))
        self._set_size(430, 140)

    def _set_size(self, w: int, h: int) -> None:
        self._adjusting = True
        self.resize(w, h)
        self._adjusting = False

    def _place(self) -> None:
        if self._custom_geometry:
            return  # the user chose a spot — keep it
        self._adjusting = True
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.top() + 24)
        self._adjusting = False

    # --- public API (called by app.py) -------------------------------------

    def show_for_input(self, chat: bool = False) -> None:
        self._reset()
        self.input.setPlaceholderText(
            "Chat with OnCUE (no screenshot)…" if chat else "Ask about your screen…"
        )
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()

    def begin_answer(self, heading: str = "") -> None:
        self.input.hide()
        self._answer_buffer = ""
        self.answer.clear()
        self.answer.show()
        if heading:
            self.set_status(heading)
        if not self._custom_geometry:
            self._set_size(430, 300)
            self._place()
        self.show()
        self.raise_()

    def show_question(self, text: str) -> None:
        """Display the user's command (typed or spoken) above the answer."""
        self.question.setText(f"🗨 {text}")
        self.question.show()

    def set_status(self, text: str) -> None:
        self.status.setText(text)
        self.status.setVisible(bool(text))

    def append_token(self, text: str) -> None:
        self._answer_buffer += text
        strip_result = strip_point_tags(self._answer_buffer)
        if strip_result != self._answer_displayed:
            self._answer_displayed = strip_result
            self.answer.setHtml(markdown_to_html(strip_result))
        sb = self.answer.verticalScrollBar()
        sb.setValue(sb.maximum())  # keep the newest text in view while streaming

    def set_system_enabled(self, enabled: bool) -> None:
        """Sync the checkbox without re-emitting (tray/timer changed it)."""
        self._system_enabled = enabled
        self.system_checkbox.blockSignals(True)
        self.system_checkbox.setChecked(enabled)
        self.system_checkbox.blockSignals(False)

    def show_confirm(self, action: str) -> None:
        self.confirm_label.setText(f"⚠ {action}")
        self.confirm_label.show()
        self.confirm_row.show()
        self.show()
        self.raise_()
        self.activateWindow()

    def finish(self) -> None:
        """Answer done — re-show the input so the user can ask a follow-up
        in the same conversation without pressing a hotkey again."""
        self.set_status("")
        self.input.clear()
        self.input.setPlaceholderText("Ask a follow-up…  (Esc to hide)")
        self.input.show()
        self.input.setFocus()

    def show_error(self, message: str) -> None:
        self.begin_answer()
        self.set_status("Something went wrong")
        self.append_token(message)
        self.finish()  # re-show the input so the user can retry

    # --- internals ----------------------------------------------------------

    def _reset(self) -> None:
        self.input.show()
        self.input.clear()
        self.question.hide()
        self.question.clear()
        self.answer.hide()
        self.answer.clear()
        self.set_status("")
        self._hide_confirm()
        if not self._custom_geometry:
            self._set_size(430, 140)
            self._place()

    def _hide_confirm(self) -> None:
        self.confirm_label.hide()
        self.confirm_row.hide()

    def _on_return(self) -> None:
        self.submitted.emit(self.input.text().strip())

    def _answer_confirm(self, allowed: bool) -> None:
        self._hide_confirm()
        self.confirmed.emit(allowed)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)

    # --- screen-capture protection ------------------------------------------

    def showEvent(self, event) -> None:
        # (re)apply on every show — the native handle/state can change
        from parakeet.screen_privacy import set_capture_protection

        set_capture_protection(self, self._content_protection)
        super().showEvent(event)

    def set_content_protection(self, enabled: bool) -> None:
        from parakeet.screen_privacy import set_capture_protection

        self._content_protection = enabled
        set_capture_protection(self, enabled)

    # --- move / resize / remember -------------------------------------------

    _EDGE_MARGIN = 12

    def _edge_at(self, pos) -> str | None:
        r = self.rect()
        on_right = pos.x() >= r.width() - self._EDGE_MARGIN
        on_bottom = pos.y() >= r.height() - self._EDGE_MARGIN
        if on_right and on_bottom:
            return "corner"
        if on_right:
            return "right"
        if on_bottom:
            return "bottom"
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._edge_at(event.position().toPoint())
            if edge:
                self._resize_edge = edge
                self._resize_start = (event.globalPosition().toPoint(), self.geometry())
            else:
                self._drag_offset = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resize_edge and event.buttons() & Qt.MouseButton.LeftButton:
            start_pos, g = self._resize_start
            delta = event.globalPosition().toPoint() - start_pos
            w, h = g.width(), g.height()
            if self._resize_edge in ("right", "corner"):
                w = max(self.minimumWidth(), g.width() + delta.x())
            if self._resize_edge in ("bottom", "corner"):
                h = max(self.minimumHeight(), g.height() + delta.y())
            self.resize(w, h)
        elif self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        else:
            # hover feedback so the resize edges are discoverable
            cursors = {
                "corner": Qt.CursorShape.SizeFDiagCursor,
                "right": Qt.CursorShape.SizeHorCursor,
                "bottom": Qt.CursorShape.SizeVerCursor,
                None: Qt.CursorShape.ArrowCursor,
            }
            self.setCursor(cursors[self._edge_at(event.position().toPoint())])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        self._resize_edge = None
        self._resize_start = None
        super().mouseReleaseEvent(event)

    def moveEvent(self, event) -> None:
        if not self._adjusting and self.isVisible():
            self._custom_geometry = True
            self._save_timer.start()
        super().moveEvent(event)

    def resizeEvent(self, event) -> None:
        if not self._adjusting and self.isVisible():
            self._custom_geometry = True
            self._save_timer.start()
        super().resizeEvent(event)

    def _persist_geometry(self) -> None:
        from parakeet.config import get_config

        g = self.geometry()
        cfg = get_config()
        cfg.overlay_geometry = f"{g.x()},{g.y()},{g.width()},{g.height()}"
        try:
            cfg.save()
        except OSError:
            pass

    def reset_position(self) -> None:
        """Back to the default top-right spot (tray menu action)."""
        from parakeet.config import get_config

        self._custom_geometry = False
        self._set_size(430, 140)
        self._place()
        cfg = get_config()
        cfg.overlay_geometry = ""
        try:
            cfg.save()
        except OSError:
            pass
