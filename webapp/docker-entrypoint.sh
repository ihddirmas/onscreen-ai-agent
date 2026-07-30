#!/bin/sh
set -e

# Apply DB migrations when an alembic directory is present.
if [ -d alembic ]; then
  reflex db migrate
fi

# Reflex requires Redis in production. When no managed Redis URL is provided,
# run redis-server in-container — but wait until it accepts connections before
# starting Reflex (otherwise Reflex exits immediately and /ping returns 503).
if [ -z "${REFLEX_REDIS_URL}" ] || [ "${REFLEX_REDIS_URL}" = "redis://localhost" ]; then
  redis-server --daemonize yes
  i=0
  while [ "$i" -lt 60 ]; do
    if redis-cli ping >/dev/null 2>&1; then
      break
    fi
    i=$((i + 1))
    sleep 0.5
  done
  if ! redis-cli ping >/dev/null 2>&1; then
    echo "redis-server did not become ready in time" >&2
    exit 1
  fi
fi

caddy start --config /app/Caddyfile

exec reflex run --env prod --backend-only --loglevel debug
