#!/usr/bin/env bash
# Start local E2E stack: Postgres schema, LiteLLM, usage API, provision test user.
set -euo pipefail
cd /workspace

if [[ ! -f .env.test ]]; then
  cp .env.test.example .env.test
fi

export GROQ_API_KEY="${GROQ_API_KEY:-$(grep -E '^GROQ_API_KEY=' .env 2>/dev/null | cut -d= -f2- | head -1)}"
export DATABASE_URL="postgresql://oncue:oncue-e2e-local@localhost/litellm"
export LITELLM_MASTER_KEY="sk-master-oncue-e2e-test"
export E2E_DATABASE_URL="postgresql://oncue:oncue-e2e-local@localhost/oncue_e2e"
export E2E_USAGE_API_PORT="3001"
export LITELLM_URL="http://localhost:4000"
export ONCUE_WEB_URL="http://localhost:3001"

echo "==> Applying E2E schema"
DB_URL="${E2E_DATABASE_URL:-postgresql://oncue:oncue-e2e-local@localhost/oncue_e2e}"
PGPASSWORD="${PGPASSWORD:-oncue-e2e-local}" psql "$DB_URL" -f scripts/e2e/schema.sql -q

echo "==> Starting LiteLLM on :4000"
pkill -f 'litellm --config' 2>/dev/null || true
sleep 1
.venv-litellm/bin/litellm --config backend/litellm-config.yaml --port 4000 \
  > /tmp/litellm-e2e.log 2>&1 &
LITELLM_PID=$!
for i in $(seq 1 30); do
  if curl -sf "http://localhost:4000/health/liveliness" >/dev/null 2>&1; then
    echo "    LiteLLM ready"
    break
  fi
  sleep 1
  if [[ $i -eq 30 ]]; then
    echo "LiteLLM failed to start; see /tmp/litellm-e2e.log"
    tail -20 /tmp/litellm-e2e.log
    exit 1
  fi
done

echo "==> Starting usage API on :${E2E_USAGE_API_PORT:-3001}"
pkill -f 'local_usage_api.py' 2>/dev/null || true
sleep 1
.venv/bin/python scripts/local_usage_api.py > /tmp/usage-api-e2e.log 2>&1 &
USAGE_PID=$!
for i in $(seq 1 15); do
  if curl -sf "http://localhost:${E2E_USAGE_API_PORT:-3001}/health" >/dev/null 2>&1; then
    echo "    Usage API ready"
    break
  fi
  sleep 1
done

echo "==> Provisioning test user"
.venv/bin/python scripts/provision_test_user.py

echo "$LITELLM_PID" > /tmp/litellm-e2e.pid
echo "$USAGE_PID" > /tmp/usage-api-e2e.pid
echo "E2E stack running (LiteLLM PID $LITELLM_PID, usage API PID $USAGE_PID)"
