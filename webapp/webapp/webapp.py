import reflex as rx
from fastapi import FastAPI

from webapp.api.usage import router as usage_router
from webapp.api.webhooks import router as webhooks_router
from webapp.pages.download import download_page
from webapp.pages.landing import landing_page
from webapp.pages.login import login_page

# Fonts referenced by webapp/webapp/styles/tokens.py's FONT dict (Inter,
# Fraunces) were declared there but never actually loaded — silently falling
# back to system-ui/Georgia this whole time. Loading them globally here.
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap",
    ],
)
app.add_page(landing_page, route="/")
app.add_page(login_page, route="/login")
app.add_page(download_page, route="/download")

# Escape hatch for server-to-server routes. Reflex's backend ASGI app
# (`app._api`) is a plain Starlette instance (0.9.7) — no public `.api`
# and no `include_router`/`add_api_route`, so we mount FastAPI sub-apps
# instead (FastAPI is valid ASGI for Starlette's `.mount()`).
_backend_app = FastAPI()
_backend_app.include_router(webhooks_router)
_backend_app.include_router(usage_router)
app._api.mount("/", _backend_app)  # noqa: SLF001 - documented escape hatch
