#!/usr/bin/env python3
"""Minimal usage API for local E2E tests (mirrors website/app/api/usage/*)."""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000").rstrip("/")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-master-oncue-e2e-test")
DATABASE_URL = os.environ.get("E2E_DATABASE_URL", "postgresql://oncue:oncue-e2e-local@localhost/oncue_e2e")
PORT = int(os.environ.get("E2E_USAGE_API_PORT", "3001"))


def _conn():
    return psycopg2.connect(DATABASE_URL)


def _key_info(token: str) -> dict | None:
    import urllib.request

    url = f"{LITELLM_URL}/key/info?key={token}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("info") or data
    except Exception:
        return None


def usage_check(token: str) -> dict:
    info = _key_info(token)
    if not info:
        return {"error": "invalid key", "_status": 403}
    user_id = (info.get("metadata") or {}).get("user_id")
    if not user_id:
        return {"error": "key not linked to a user", "_status": 403}

    with _conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "select tier, session_count, trial_used from profiles where id = %s",
            (user_id,),
        )
        profile = cur.fetchone()

    if not profile:
        return {
            "can_start": True,
            "tier": "free",
            "session_count": 0,
            "trial_remaining": 1,
        }

    tier = profile["tier"]
    session_count = profile["session_count"] or 0
    trial_used = profile["trial_used"]
    if tier == "pro":
        can_start = True
        is_trial = False
    elif tier == "trial":
        can_start = session_count < 1
        is_trial = True
    else:
        # free tier: one hosted trial session, then upgrade required
        is_trial = not trial_used
        can_start = not trial_used and session_count < 1

    return {
        "can_start": can_start,
        "tier": "trial" if is_trial else tier,
        "session_count": session_count,
        "trial_remaining": max(0, 1 - session_count) if is_trial or not trial_used else 0,
    }


def usage_report(body: dict) -> dict:
    token = body.get("token")
    event_type = body.get("event_type")
    session_id = body.get("session_id")
    if not token or not event_type or not session_id:
        return {"error": "token, event_type, session_id required", "_status": 400}

    info = _key_info(token)
    if not info:
        return {"error": "invalid key", "_status": 403}
    user_id = (info.get("metadata") or {}).get("user_id")
    if not user_id:
        return {"error": "key not linked to a user", "_status": 403}

    with _conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "select tier, trial_used, session_count from profiles where id = %s",
            (user_id,),
        )
        profile = cur.fetchone()
        is_trial = (
            profile
            and (profile["tier"] == "trial" or (profile["tier"] == "free" and not profile["trial_used"]))
        ) or not profile
        tier = "trial" if is_trial else (profile["tier"] if profile else "free")

        try:
            cur.execute(
                """insert into usage_ledger
                   (user_id, session_id, event_type, model_used, tokens_in, tokens_out, tier, cost_usd)
                   values (%s, %s, %s, %s, %s, %s, %s, 0)""",
                (
                    user_id,
                    session_id,
                    event_type,
                    body.get("model_used"),
                    body.get("tokens_in") or 0,
                    body.get("tokens_out") or 0,
                    tier,
                ),
            )
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            if "trial_session_limit_reached" in str(e):
                return {"error": "trial_limit_reached", "_status": 403}
            return {"error": f"ledger insert failed: {e}", "_status": 500}

    return {"ok": True}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[usage-api] {fmt % args}\n")

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"ok": True})
            return
        if path == "/mock/rag":
            self._json(200, {"status": "mock", "message": "RAG stub for E2E"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        if path == "/api/usage/check":
            result = usage_check(body.get("token", ""))
            status = result.pop("_status", 200)
            self._json(status, result)
            return
        if path == "/api/usage/report":
            result = usage_report(body)
            status = result.pop("_status", 200)
            self._json(status, result)
            return
        self._json(404, {"error": "not found"})


def main() -> None:
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"E2E usage API on http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
