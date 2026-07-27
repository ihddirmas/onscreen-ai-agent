"""Session state: sign up / sign in / sign out, Google OAuth kick-off, and
the Supabase session cookie. All business logic (the actual Supabase calls)
is a thin pass-through to webapp.services.supabase — this class only
orchestrates the request/response cycle and UI-visible state."""
from __future__ import annotations

import reflex as rx

from webapp.services.supabase import anon_client


class AuthState(rx.State):
    access_token: str = rx.Cookie("", name="pk_session")
    user_id: str = rx.Cookie("", name="pk_user_id")
    email: str = ""
    error: str = ""
    busy: bool = False

    @rx.var
    def is_logged_in(self) -> bool:
        return bool(self.access_token)

    async def sign_in(self, form_data: dict):
        self.busy = True
        self.error = ""
        yield
        try:
            client = anon_client()
            result = client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            self.access_token = result.session.access_token
            self.user_id = result.user.id
            self.email = result.user.email or ""
        except Exception as exc:  # noqa: BLE001 - surfaced to the user below, never swallowed
            self.error = str(exc)
        finally:
            self.busy = False
        if self.access_token:
            yield rx.redirect("/dashboard")

    async def sign_up(self, form_data: dict):
        self.busy = True
        self.error = ""
        yield
        try:
            client = anon_client()
            result = client.auth.sign_up(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if result.session:
                self.access_token = result.session.access_token
                self.user_id = result.user.id
                self.email = result.user.email or ""
            else:
                self.error = "Account created. Check your inbox to confirm your email."
        except Exception as exc:  # noqa: BLE001
            self.error = str(exc)
        finally:
            self.busy = False
        if self.access_token:
            yield rx.redirect("/dashboard")

    def sign_in_with_google(self):
        client = anon_client()
        # `self.router.page.host` is deprecated as of Reflex 0.8.1 (removed in
        # 1.0) in favor of `self.router.url.origin`, which is the currently
        # installed version's (0.9.7) recommended replacement with the same
        # value (scheme + netloc of the current page).
        result = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": f"{self.router.url.origin}/dashboard"},
            }
        )
        return rx.redirect(result.url)

    def sign_out(self):
        self.access_token = ""
        self.user_id = ""
        self.email = ""
        return rx.redirect("/login")
