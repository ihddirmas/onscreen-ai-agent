#!/usr/bin/env bash
# Local stack smoke test — mirrors DEPLOY.md steps 2–3 without Railway/Render/Supabase.
# Prerequisites: GROQ_API_KEY in env, Postgres on localhost, LiteLLM venv at .venv-litellm
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MASTER_KEY="${LITELLM_MASTER_KEY:-sk-master-local-test}"
LITELLM_PORT="${LITELLM_PORT:-4000}"
DATABASE_URL="${DATABASE_URL:-postgresql://oncue:oncue@localhost/litellm}"

echo "== Step 1: LiteLLM health =="
curl -sf "http://127.0.0.1:${LITELLM_PORT}/health/liveliness" >/dev/null
echo "OK"

echo "== Step 2: Mint virtual key =="
KEY=$(curl -sf -X POST "http://127.0.0.1:${LITELLM_PORT}/key/generate" \
  -H "Authorization: Bearer ${MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"models":["oncue-default"],"max_budget":1,"budget_duration":"30d"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['key'])")
echo "minted: ${KEY:0:24}..."

echo "== Step 3: Chat completion =="
curl -sf "http://127.0.0.1:${LITELLM_PORT}/v1/chat/completions" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"oncue-default","messages":[{"role":"user","content":"hi"}]}' \
  | python3 -c "import sys,json; print('reply:', json.load(sys.stdin)['choices'][0]['message']['content'][:80])"

echo "== Step 4: Webapp litellm service =="
cd "$ROOT/webapp"
LITELLM_URL="http://127.0.0.1:${LITELLM_PORT}" LITELLM_MASTER_KEY="$MASTER_KEY" \
  .venv/bin/python -c "from webapp.services.litellm import mint_key,get_spend; k=mint_key('smoke-user','free'); print('webapp key', k[:20]+'...', 'spend', get_spend(k))"

echo "== All local smoke steps passed =="
