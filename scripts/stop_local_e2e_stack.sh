#!/usr/bin/env bash
set -euo pipefail
pkill -f 'litellm --config' 2>/dev/null || true
pkill -f 'local_usage_api.py' 2>/dev/null || true
rm -f /tmp/litellm-e2e.pid /tmp/usage-api-e2e.pid
echo "Stopped local E2E stack"
