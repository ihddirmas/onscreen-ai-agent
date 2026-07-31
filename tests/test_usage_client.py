"""Usage API client helpers."""
from unittest.mock import patch

from oncue import usage


def test_check_session_fail_open_when_offline():
    with patch.object(usage, "_post", return_value=None):
        result = usage.check_session()
    assert result["can_start"] is True


def test_report_session_start_fail_open_when_offline():
    with patch.object(usage, "_post", return_value=None):
        assert usage.report_session_start() is True


def test_report_session_start_blocked_on_trial_limit():
    with patch.object(usage, "_post", return_value={"error": "trial_limit_reached"}):
        assert usage.report_session_start() is False


def test_report_session_start_ok():
    with patch.object(usage, "_post", return_value={"ok": True}):
        assert usage.report_session_start() is True
