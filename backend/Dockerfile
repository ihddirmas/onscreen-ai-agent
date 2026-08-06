# Parakeet hosted backend — LiteLLM proxy.
# Set env on the host: GROQ_API_KEY (+ ANTHROPIC/OPENAI for production),
# LITELLM_MASTER_KEY, DATABASE_URL (Postgres).
FROM ghcr.io/berriai/litellm:main-latest

COPY litellm-config.yaml /app/config.yaml

# Honor the platform's assigned port (Render sets $PORT); default 4000 for
# local `docker run` and Railway. Shell form so ${PORT:-4000} is expanded.
EXPOSE 4000
CMD litellm --config /app/config.yaml --port ${PORT:-4000}
