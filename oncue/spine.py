"""Phase-0 spine: hotkey -> screenshot -> model -> streamed answer to stdout.

Usage:
  python -m oncue.spine --now                # capture immediately
  python -m oncue.spine                      # wait for the capture hotkey
  python -m oncue.spine --question "..."     # custom question
Acceptance: prints a streaming answer describing what's on screen (Groq free tier).
"""

from __future__ import annotations

import argparse
import threading

from oncue.capture import screenshot_png
from oncue.config import get_config
from oncue.agent.router import build_message, get_model
from oncue.usage import report_inference, report_session_start

DEFAULT_QUESTION = "Describe what's on my screen and answer anything it's asking. Be concise."


def run_once(question: str) -> None:
    cfg = get_config()
    if cfg.provider == "hosted" and cfg.web_url:
        report_session_start()
    print(f"[OnCUE] provider={cfg.provider}  capturing screen...")
    png = screenshot_png()
    model = get_model()
    print("[OnCUE] streaming answer:\n")
    answer_parts: list[str] = []
    for chunk in model.stream([build_message(question, png)]):
        text = chunk.content
        if isinstance(text, list):  # anthropic-style content blocks
            text = "".join(b.get("text", "") for b in text if isinstance(b, dict))
        if text:
            answer_parts.append(text)
            print(text, end="", flush=True)
    print("\n")
    if cfg.provider == "hosted" and cfg.web_url:
        full = "".join(answer_parts)
        report_inference(
            model_used=cfg.hosted_model,
            tokens_out=len(full) // 4,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="OnCUE phase-0 spine")
    parser.add_argument("--now", action="store_true", help="capture immediately, no hotkey")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    cfg = get_config()
    cfg.apply_env()

    if args.now:
        run_once(args.question)
        return

    from oncue.hotkeys import HotkeyManager

    done = threading.Event()

    def on_hotkey():
        try:
            run_once(args.question)
        finally:
            done.set()

    hk = HotkeyManager()
    hk.register(cfg.capture_hotkey, on_hotkey)
    hk.start()
    print(f"[OnCUE] press {cfg.capture_hotkey} to capture (Ctrl+C to quit)")
    try:
        done.wait()
    except KeyboardInterrupt:
        pass
    hk.stop()


if __name__ == "__main__":
    main()
