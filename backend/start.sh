#!/usr/bin/env bash
# Render-native LiteLLM start (no Docker). Prisma client is generated at build time.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-4000}"
export DISABLE_SCHEMA_UPDATE="${DISABLE_SCHEMA_UPDATE:-true}"
exec litellm --config litellm-config.yaml --host 0.0.0.0 --port "$PORT"
