#!/usr/bin/env bash
# Render build script for LiteLLM proxy (Python, no Docker).
set -euo pipefail
cd "$(dirname "$0")"
pip install -r requirements.txt
SCHEMA="$(python -c "import litellm, os; print(os.path.join(os.path.dirname(litellm.__file__), 'proxy', 'schema.prisma'))")"
prisma generate --schema "$SCHEMA"
