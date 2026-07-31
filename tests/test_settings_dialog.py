"""Settings dialog structure and section navigation."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_settings_dialog_has_all_sections(qapp):
    from oncue.ui.settings import SettingsDialog

    dialog = SettingsDialog()
    sections = dialog._section_widgets
    assert set(sections) == {
        "quick_start",
        "provider",
        "api_keys",
        "hosted",
        "speech",
        "behavior",
    }


def test_settings_fields_exist(qapp):
    from oncue.ui.settings import SettingsDialog

    d = SettingsDialog()
    assert d.provider.count() == 5
    assert d.capture_hotkey.text()
    assert d.voice_hotkey.text()
    assert d.dictate_hotkey.text()
    assert d.chat_hotkey.text()
    assert d.meeting_hotkey.text()
    assert d.content_protection.isCheckable()
    assert d.system_tools_enabled.isCheckable()
    assert d.confirm_actions.isCheckable()
    assert d.stt_language.count() == 4
    assert d.stt_backend.count() == 3


def test_scroll_to_section_no_crash(qapp):
    from oncue.ui.settings import SettingsDialog

    d = SettingsDialog()
    for name in d._section_widgets:
        d.scroll_to_section(name)


def test_feature_guide_builds(qapp):
    from oncue.ui.feature_guide import FeatureGuideDialog, _SECTIONS

    assert len(_SECTIONS) >= 9
    guide = FeatureGuideDialog()
    assert guide.windowTitle() == "OnCUE — Feature guide"
