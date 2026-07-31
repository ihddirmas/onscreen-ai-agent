"""E2E hosted flow tests against local stack (.env.test required).

Run:
  bash scripts/start_local_e2e_stack.sh
  .venv/bin/pytest tests/test_e2e_hosted_flow.py -v
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENV_TEST = ROOT / ".env.test"


def _load_env_test() -> dict[str, str]:
    if not ENV_TEST.exists():
        pytest.skip(".env.test missing — run scripts/start_local_e2e_stack.sh first")
    out: dict[str, str] = {}
    for line in ENV_TEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _post(url: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


@pytest.fixture(scope="module", autouse=True)
def reset_trial_state():
    """Fresh trial before E2E usage tests."""
    import subprocess

    subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/provision_test_user.py")],
        check=True,
        cwd=ROOT,
    )
    yield


@pytest.fixture(scope="module")
def e2e_env():
    env = _load_env_test()
    web = env.get("ONCUE_WEB_URL", "http://localhost:3001").rstrip("/")
    token = env.get("ONCUE_TOKEN", "")
    if not token:
        pytest.skip("ONCUE_TOKEN not set in .env.test")
    return {"web": web, "token": token, "backend": env.get("ONCUE_BACKEND_URL", "")}


class TestHostedUsageAPI:
    def test_health(self, e2e_env):
        with urlopen(f"{e2e_env['web']}/health", timeout=5) as resp:
            assert resp.status == 200

    def test_trial_check_allows_first_session(self, e2e_env):
        result = _post(f"{e2e_env['web']}/api/usage/check", {"token": e2e_env["token"]})
        assert result.get("can_start") is True
        assert result.get("trial_remaining", 0) >= 0

    def test_session_start_and_block_second(self, e2e_env):
        sid = str(uuid.uuid4())
        start = _post(
            f"{e2e_env['web']}/api/usage/report",
            {"token": e2e_env["token"], "event_type": "session_start", "session_id": sid},
        )
        assert start.get("ok") is True

        inference = _post(
            f"{e2e_env['web']}/api/usage/report",
            {
                "token": e2e_env["token"],
                "event_type": "inference",
                "session_id": sid,
                "model_used": "oncue-default",
                "tokens_in": 100,
                "tokens_out": 50,
            },
        )
        assert inference.get("ok") is True

        check = _post(f"{e2e_env['web']}/api/usage/check", {"token": e2e_env["token"]})
        # After first trial session, second should be blocked
        assert check.get("can_start") is False


class TestDeepLinkProtocol:
    def test_connect_applies_hosted_config(self, e2e_env):
        from oncue.config import get_config
        from oncue.protocol import apply_url
        from urllib.parse import quote

        token = e2e_env["token"]
        web = e2e_env["web"]
        rag = f"{web}/mock/rag"
        backend = e2e_env["backend"]
        url = (
            f"oncue://connect?token={quote(token)}&web={quote(web)}"
            f"&rag={quote(rag)}&backend={quote(backend)}"
        )
        with patch("oncue.protocol.set_config"), patch.object(get_config(), "save"):
            status = apply_url(url)
        assert status == "Connected to your OnCUE account"
        cfg = get_config()
        assert cfg.provider == "hosted"
        assert cfg.oncue_token == token
        assert cfg.web_url == web


class TestUsageClientIntegration:
    def test_check_session_live(self, e2e_env):
        from oncue import usage
        from oncue.config import Config, set_config

        cfg = Config(
            provider="hosted",
            oncue_token=e2e_env["token"],
            web_url=e2e_env["web"],
            backend_url=e2e_env["backend"],
        )
        set_config(cfg)
        result = usage.check_session()
        assert "can_start" in result
