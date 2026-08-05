"""E2E-style tests for the Overlay widget: real widgets, real key/mouse
events via qtbot, real signal wiring — only the OS-level effects outside Qt
(screen capture protection) are exercised through the real code path since
Overlay.showEvent calls into oncue.screen_privacy directly."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from oncue.ui.overlay import Overlay, markdown_to_html


def _overlay(qtbot, **kwargs) -> Overlay:
    ov = Overlay(**kwargs)
    qtbot.addWidget(ov)
    return ov


def test_show_for_input_displays_empty_focused_input(qtbot):
    ov = _overlay(qtbot)

    ov.show_for_input()

    assert ov.isVisible()
    assert ov.input.text() == ""
    qtbot.waitUntil(lambda: ov.input.hasFocus(), timeout=2000)


def test_show_for_input_chat_mode_uses_chat_placeholder(qtbot):
    ov = _overlay(qtbot)

    ov.show_for_input(chat=True)

    assert "Chat with OnCUE" in ov.input.placeholderText()


def test_typing_and_enter_emits_submitted_with_stripped_text(qtbot):
    ov = _overlay(qtbot)
    ov.show_for_input()

    with qtbot.waitSignal(ov.submitted, timeout=1000) as blocker:
        qtbot.keyClicks(ov.input, "  hello world  ")
        qtbot.keyClick(ov.input, Qt.Key.Key_Return)

    assert blocker.args == ["hello world"]


def test_escape_hides_overlay_and_emits_cancelled(qtbot):
    ov = _overlay(qtbot)
    ov.show_for_input()

    with qtbot.waitSignal(ov.cancelled, timeout=1000):
        qtbot.keyClick(ov, Qt.Key.Key_Escape)

    assert not ov.isVisible()


def test_begin_answer_hides_input_and_reveals_answer_pane(qtbot):
    ov = _overlay(qtbot)
    ov.show_for_input()

    ov.begin_answer("Thinking…")

    assert not ov.input.isVisible()
    assert ov.answer.isVisible()
    assert ov.status.text() == "Thinking…"


def test_show_question_displays_the_users_command(qtbot):
    ov = _overlay(qtbot)
    ov.show()  # isVisible() on a child requires the top-level to be shown too

    ov.show_question("what's this error?")

    assert ov.question.isVisible()
    assert "what's this error?" in ov.question.text()


def test_append_token_streams_into_the_answer_pane(qtbot):
    ov = _overlay(qtbot)
    ov.begin_answer()

    ov.append_token("Hello ")
    ov.append_token("world")

    assert "Hello world" in ov.answer.toPlainText()


def test_finish_clears_input_and_shows_followup_placeholder(qtbot):
    ov = _overlay(qtbot)
    ov.begin_answer()
    ov.append_token("some answer")

    ov.finish()

    assert ov.input.isVisible()
    assert ov.input.text() == ""
    assert "follow-up" in ov.input.placeholderText()


def test_show_error_renders_message_and_reopens_input_for_retry(qtbot):
    ov = _overlay(qtbot)

    ov.show_error("Something went wrong: 500")

    assert "Something went wrong: 500" in ov.answer.toPlainText()
    assert ov.input.isVisible()


def test_confirm_allow_click_emits_confirmed_true_and_hides_row(qtbot):
    ov = _overlay(qtbot)
    ov.show_confirm("Open browser to example.com?")
    allow_btn = ov.confirm_row.findChild(QPushButton, "allow")

    with qtbot.waitSignal(ov.confirmed, timeout=1000) as blocker:
        qtbot.mouseClick(allow_btn, Qt.MouseButton.LeftButton)

    assert blocker.args == [True]
    assert not ov.confirm_row.isVisible()
    assert not ov.confirm_label.isVisible()


def test_confirm_deny_click_emits_confirmed_false(qtbot):
    ov = _overlay(qtbot)
    ov.show_confirm("Delete this file?")
    deny_btn = ov.confirm_row.findChild(QPushButton, "deny")

    with qtbot.waitSignal(ov.confirmed, timeout=1000) as blocker:
        qtbot.mouseClick(deny_btn, Qt.MouseButton.LeftButton)

    assert blocker.args == [False]


def test_system_checkbox_toggle_emits_system_toggled(qtbot):
    ov = _overlay(qtbot, system_enabled=True)

    with qtbot.waitSignal(ov.system_toggled, timeout=1000) as blocker:
        ov.system_checkbox.setChecked(False)

    assert blocker.args == [False]


def test_set_system_enabled_syncs_checkbox_without_reemitting(qtbot):
    ov = _overlay(qtbot)
    seen = []
    ov.system_toggled.connect(seen.append)

    ov.set_system_enabled(False)

    assert ov.system_checkbox.isChecked() is False
    assert seen == []  # programmatic sync (tray/timer) must not re-trigger the signal


def test_reset_between_turns_hides_question_and_answer(qtbot):
    ov = _overlay(qtbot)
    ov.begin_answer()
    ov.show_question("first question")
    ov.append_token("first answer")

    ov.show_for_input()  # calls _reset() internally

    assert not ov.question.isVisible()
    assert not ov.answer.isVisible()
    assert ov.input.text() == ""


def test_markdown_to_html_wraps_fenced_code_in_a_code_block():
    html = markdown_to_html("before\n```python\nprint(1)\n```\nafter")

    assert "<pre" in html
    assert "print(1)" in html
    assert "before" in html and "after" in html


def test_markdown_to_html_styles_inline_code():
    html = markdown_to_html("use `foo()` here")

    assert "<code" in html
    assert "foo()" in html
