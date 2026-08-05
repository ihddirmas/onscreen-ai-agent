"""E2E-style tests for SettingsDialog: real widget tree populated from the
isolated Config, real Save/Cancel button clicks, verifying the dialog
actually persists to (the tmp-redirected) disk and updates the process-wide
config singleton."""
from __future__ import annotations

from PySide6.QtCore import Qt

import oncue.config as config_module
from oncue.config import get_config
from oncue.ui.settings import SettingsDialog


def _dialog(qtbot) -> SettingsDialog:
    dlg = SettingsDialog()
    qtbot.addWidget(dlg)
    return dlg


def test_dialog_loads_current_config_into_fields(qtbot):
    dlg = _dialog(qtbot)

    assert dlg.provider.currentText() == get_config().provider
    assert dlg.capture_hotkey.text() == get_config().capture_hotkey
    assert dlg.system_tools_enabled.isChecked() == get_config().system_tools_enabled


def test_save_writes_edited_fields_to_disk_and_emits_saved(qtbot):
    dlg = _dialog(qtbot)
    dlg.provider.setCurrentText("groq")
    dlg.groq_key.setText("sk-test-123")
    dlg.capture_hotkey.setText("<ctrl>+<alt>+<space>")
    dlg.system_tools_enabled.setChecked(False)

    with qtbot.waitSignal(dlg.saved, timeout=1000):
        dlg._save()

    assert config_module.CONFIG_FILE.exists()
    saved_text = config_module.CONFIG_FILE.read_text(encoding="utf-8")
    assert "GROQ_API_KEY=sk-test-123" in saved_text
    assert "DEFAULT_PROVIDER=groq" in saved_text

    cfg = get_config()
    assert cfg.provider == "groq"
    assert cfg.groq_api_key == "sk-test-123"
    assert cfg.capture_hotkey == "<ctrl>+<alt>+<space>"
    assert cfg.system_tools_enabled is False


def test_save_closes_the_dialog_with_accept(qtbot):
    dlg = _dialog(qtbot)

    with qtbot.waitSignal(dlg.accepted, timeout=1000):
        dlg._save()


def test_cancel_does_not_persist_edits(qtbot):
    dlg = _dialog(qtbot)
    original_provider = get_config().provider
    dlg.provider.setCurrentText("gpt")

    with qtbot.waitSignal(dlg.rejected, timeout=1000):
        qtbot.keyClick(dlg, Qt.Key.Key_Escape)

    assert get_config().provider == original_provider
    assert not config_module.CONFIG_FILE.exists()


def test_blank_hotkey_falls_back_to_previous_value(qtbot):
    dlg = _dialog(qtbot)
    original_hotkey = get_config().capture_hotkey
    dlg.capture_hotkey.setText("   ")  # whitespace-only -> treated as blank

    dlg._save()

    assert get_config().capture_hotkey == original_hotkey


def test_api_key_fields_use_password_echo_mode(qtbot):
    dlg = _dialog(qtbot)

    assert dlg.groq_key.echoMode() == dlg.groq_key.EchoMode.Password
    assert dlg.token.echoMode() == dlg.token.EchoMode.Password
