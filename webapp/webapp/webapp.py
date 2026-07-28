import reflex as rx
from fastapi import FastAPI

from webapp.api.webhooks import router as webhooks_router
from webapp.pages.download import download_page
from webapp.pages.landing import landing_page
from webapp.pages.login import login_page

app = rx.App()
app.add_page(landing_page, route="/")
app.add_page(login_page, route="/login")
app.add_page(download_page, route="/download")

# Webhook escape hatch. Reflex's backend ASGI app (`app._api`) is a plain
# Starlette instance in the installed version (0.9.7) — there is no public
# `app.api` and no `include_router`/`add_api_route` on Starlette itself.
# Wrap the webhook routes in a small FastAPI sub-app and mount that instead
# (verified: FastAPI apps are valid ASGI sub-apps for Starlette's `.mount`).
_webhooks_app = FastAPI()
_webhooks_app.include_router(webhooks_router)
app._api.mount("/", _webhooks_app)  # noqa: SLF001 - documented escape hatch, see above
