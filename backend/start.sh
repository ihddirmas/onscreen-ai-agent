#!/usr/bin/env bash
# Render-native LiteLLM start (no Docker). Copies config and starts proxy.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-4000}"
exec litellm --config litellm-config.yaml --host 0.0.0.0 --port "$PORT"
