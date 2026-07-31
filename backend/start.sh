#!/usr/bin/env bash
# Render-native LiteLLM start (no Docker). Bind quickly; migrations run at build time.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-4000}"
SCHEMA="$(python -c "import litellm, os; print(os.path.join(os.path.dirname(litellm.__file__), 'proxy', 'schema.prisma'))")"
prisma generate --schema "$SCHEMA"
export DISABLE_SCHEMA_UPDATE="${DISABLE_SCHEMA_UPDATE:-true}"
exec litellm --config litellm-config.yaml --host 0.0.0.0 --port "$PORT"
