"""E2E-style tests for OnboardingDialog: the first-run choice between a
hosted trial and bring-your-own-key. webbrowser.open is the only mocked
boundary — it would otherwise pop a real browser window during the test run."""
from __future__ import annotations

from unittest.mock import patch

from PySide6.QtCore import Qt

from oncue.config import get_config, set_config
from oncue.ui.onboarding import OnboardingDialog


def _dialog(qtbot) -> OnboardingDialog:
    dlg = OnboardingDialog()
    qtbot.addWidget(dlg)
    dlg.show()  # non-modal show (not exec()) — isVisible() needs the top-level shown
    return dlg


def test_trial_button_with_web_url_opens_login_and_accepts(qtbot):
    cfg = get_config()
    cfg.web_url = "https://app.oncue.example.com"
    set_config(cfg)
    dlg = _dialog(qtbot)

    with patch("oncue.ui.onboarding.webbrowser.open") as mock_open:
        with qtbot.waitSignal(dlg.accepted, timeout=1000):
            qtbot.mouseClick(dlg._trial_btn, Qt.MouseButton.LeftButton)

    mock_open.assert_called_once_with("https://app.oncue.example.com/login")


def test_trial_button_without_web_url_shows_status_and_stays_open(qtbot):
    cfg = get_config()
    cfg.web_url = ""
    set_config(cfg)
    dlg = _dialog(qtbot)

    with patch("oncue.ui.onboarding.webbrowser.open") as mock_open:
        qtbot.mouseClick(dlg._trial_btn, Qt.MouseButton.LeftButton)

    mock_open.assert_not_called()
    assert dlg._status.isVisible()
    assert "own API key" in dlg._status.text()
    assert dlg.isVisible()  # not dismissed — the user still needs to act


def test_own_key_button_emits_open_settings_and_accepts(qtbot):
    dlg = _dialog(qtbot)
    key_btn = [
        w for w in dlg.findChildren(type(dlg._trial_btn))
        if w.text() == "I have my own API key"
    ][0]

    with qtbot.waitSignal(dlg.open_settings, timeout=1000):
        with qtbot.waitSignal(dlg.accepted, timeout=1000):
            qtbot.mouseClick(key_btn, Qt.MouseButton.LeftButton)
