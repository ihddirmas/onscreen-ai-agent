import reflex as rx
from fastapi import FastAPI

from webapp.api.webhooks import router as webhooks_router


def index() -> rx.Component:
    return rx.center(rx.text("Parakeet — under construction"), height="100vh")


app = rx.App()
app.add_page(index, route="/")

# Webhook escape hatch. Reflex's backend ASGI app (`app._api`) is a plain
# Starlette instance in the installed version (0.9.7) — there is no public
# `app.api` and no `include_router`/`add_api_route` on Starlette itself.
# Wrap the webhook routes in a small FastAPI sub-app and mount that instead
# (verified: FastAPI apps are valid ASGI sub-apps for Starlette's `.mount`).
_webhooks_app = FastAPI()
_webhooks_app.include_router(webhooks_router)
app._api.mount("/", _webhooks_app)  # noqa: SLF001 - documented escape hatch, see above
