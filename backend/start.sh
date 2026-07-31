#!/usr/bin/env bash
# Render-native LiteLLM start (no Docker). Copies config and starts proxy.
set -euo pipefail
cd "$(dirname "$0")"
exec litellm --config litellm-config.yaml --port "${PORT:-4000}"
