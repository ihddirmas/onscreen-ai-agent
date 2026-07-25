"""Phase-0 spine: hotkey -> screenshot -> model -> streamed answer to stdout.

Usage:
  python -m parakeet.spine --now                # capture immediately
  python -m parakeet.spine                      # wait for the capture hotkey
  python -m parakeet.spine --question "..."     # custom question
Acceptance: prints a streaming answer describing what's on screen (Groq free tier).
"""

from __future__ import annotations

import argparse
import threading

from parakeet.capture import screenshot_png
from parakeet.config import get_config
from parakeet.agent.router import build_message, get_model

DEFAULT_QUESTION = "Describe what's on my screen and answer anything it's asking. Be concise."


def run_once(question: str) -> None:
    cfg = get_config()
    print(f"[parakeet] provider={cfg.provider}  capturing screen...")
    png = screenshot_png()
    model = get_model()
    print("[parakeet] streaming answer:\n")
    for chunk in model.stream([build_message(question, png)]):
        text = chunk.content
        if isinstance(text, list):  # anthropic-style content blocks
            text = "".join(b.get("text", "") for b in text if isinstance(b, dict))
        if text:
            print(text, end="", flush=True)
    print("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parakeet phase-0 spine")
    parser.add_argument("--now", action="store_true", help="capture immediately, no hotkey")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    cfg = get_config()
    cfg.apply_env()

    if args.now:
        run_once(args.question)
        return

    from parakeet.hotkeys import HotkeyManager

    done = threading.Event()

    def on_hotkey():
        try:
            run_once(args.question)
        finally:
            done.set()

    hk = HotkeyManager()
    hk.register(cfg.capture_hotkey, on_hotkey)
    hk.start()
    print(f"[parakeet] press {cfg.capture_hotkey} to capture (Ctrl+C to quit)")
    try:
        done.wait()
    except KeyboardInterrupt:
        pass
    hk.stop()


if __name__ == "__main__":
    main()
