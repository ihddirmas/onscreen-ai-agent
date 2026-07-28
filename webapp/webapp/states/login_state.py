"""Login-page-only UI state: which mode (sign in / sign up) the single form
is currently in. Kept separate from AuthState so that UI-only concern
doesn't leak into every other consumer of AuthState (dashboard, etc.)."""
from __future__ import annotations

from webapp.states.auth_state import AuthState


class LoginState(AuthState):
    mode: str = "in"  # "in" | "up"

    def toggle_mode(self):
        self.mode = "up" if self.mode == "in" else "in"
        self.error = ""

    def submit(self, form_data: dict):
        # Delegates to the actual auth call for the current mode — Reflex
        # lets an event handler return another handler's call to chain to it.
        if self.mode == "in":
            return LoginState.sign_in(form_data)
        return LoginState.sign_up(form_data)
