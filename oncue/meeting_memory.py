"""Persistent standup / meeting notes across OnCUE sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _memory_path() -> Path:
    from platformdirs import user_config_dir

    return Path(user_config_dir("OnCUE", appauthor=False)) / "meeting_memory.json"
_MAX_TURNS = 80


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_memory() -> dict[str, Any]:
    path = _memory_path()
    if not path.exists():
        return {"turns": [], "standups": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"turns": [], "standups": []}


def save_memory(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_turn(question: str, answer: str) -> None:
    data = load_memory()
    turns: list[dict[str, str]] = data.setdefault("turns", [])
    turns.append(
        {
            "at": _now_iso(),
            "question": question.strip()[:800],
            "answer": answer.strip()[:3000],
        }
    )
    if len(turns) > _MAX_TURNS:
        data["turns"] = turns[-_MAX_TURNS:]
    save_memory(data)


def format_for_prompt(max_turns: int = 12) -> str:
    data = load_memory()
    turns = data.get("turns") or []
    standups = data.get("standups") or []
    lines: list[str] = []
    if standups:
        last = standups[-1]
        lines.append("Last recorded standup summary:")
        for key in ("priorities", "blockers", "decisions", "people", "notes"):
            val = last.get(key)
            if val:
                lines.append(f"  {key}: {val}")
    if turns:
        lines.append("Recent meeting / interview turns (reference naturally):")
        for t in turns[-max_turns:]:
            q = t.get("question", "")
            a = t.get("answer", "")
            if q:
                lines.append(f"  - Q: {q}")
            if a:
                snippet = a.replace("\n", " ")[:240]
                lines.append(f"    A: {snippet}")
    if not lines:
        return ""
    return "\n".join(lines)
