# Single-container Reflex deployment for Railway / Render / Heroku.
# Adapted from reflex-dev/reflex's official production-one-port/Dockerfile.
# Builder stage: install deps, compile frontend.
# Runner stage: Python + Caddy + optional redis on one exposed port.
# On Railway: add a managed Redis add-on and set REFLEX_REDIS_URL=${{Redis.REDIS_URL}}
# to skip the in-container redis-server (recommended for production).
ARG PORT=8080
ARG API_URL

FROM python:3.13 AS builder

RUN mkdir -p /app/.web
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY rxconfig.py ./
RUN reflex init

COPY *.web/bun.lockb *.web/package.json .web/
RUN if [ -f .web/bun.lockb ]; then cd .web && ~/.local/share/reflex/bun/bin/bun install --frozen-lockfile; fi

COPY . .

ARG PORT API_URL
RUN REFLEX_API_URL=${API_URL:-http://localhost:$PORT} reflex export --loglevel debug --frontend-only --no-zip && mv .web/build/client/* /srv/ && rm -rf .web


FROM python:3.13-slim

RUN apt-get update -y && apt-get install -y caddy redis-server && rm -rf /var/lib/apt/lists/*

ARG PORT API_URL
ENV PATH="/app/.venv/bin:$PATH" PORT=$PORT REFLEX_API_URL=${API_URL:-http://localhost:$PORT} REFLEX_REDIS_URL=redis://localhost PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /srv /srv

RUN chmod +x /app/docker-entrypoint.sh

STOPSIGNAL SIGKILL

EXPOSE $PORT

ENTRYPOINT ["/app/docker-entrypoint.sh"]
