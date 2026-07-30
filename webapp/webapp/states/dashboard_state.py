"""Dashboard state: Parakeet key + credit meter, reference documents,
preferences, and the onboarding checklist. All Supabase/LiteLLM calls are
thin pass-throughs to webapp.services.* — this class only orchestrates."""
from __future__ import annotations

import reflex as rx

from webapp.services.litellm import get_spend, mint_key
from webapp.services.supabase import admin_client
from webapp.states.auth_state import AuthState


class DashboardState(AuthState):
    tier: str = "free"
    oncue_key: str = ""
    spend: float = 0.0
    max_budget: float = 0.0
    persona: str = ""
    preferences: str = ""
    docs: list[dict] = []
    ck_downloaded: bool = rx.Cookie(False, name="ck_downloaded")
    ck_opened_app: bool = rx.Cookie(False, name="ck_opened_app")

    @rx.var
    def credit_pct(self) -> float:
        if self.max_budget <= 0:
            return 0.0
        return min(100.0, (self.spend / self.max_budget) * 100)

    @rx.var
    def has_ready_doc(self) -> bool:
        return any(d.get("status") == "ready" for d in self.docs)

    @rx.var
    def checklist_complete(self) -> bool:
        return self.ck_downloaded and self.ck_opened_app and self.has_ready_doc

    @rx.var
    def deep_link(self) -> str:
        if not self.oncue_key:
            return "#"
        return f"oncue://connect?token={self.oncue_key}"

    async def load_dashboard(self):
        if not self.is_logged_in:
            yield rx.redirect("/login")
            return
        admin = admin_client()
        profile = (
            admin.table("profiles")
            .select("tier, litellm_key, persona, preferences")
            .eq("id", self.user_id)
            .maybe_single()
            .execute()
            .data
            or {}
        )
        self.tier = profile.get("tier", "free")
        self.persona = profile.get("persona") or ""
        self.preferences = profile.get("preferences") or ""
        self.oncue_key = profile.get("litellm_key") or ""
        if not self.oncue_key:
            self.oncue_key = mint_key(self.user_id, self.tier)
            admin.table("profiles").update({"litellm_key": self.oncue_key}).eq(
                "id", self.user_id
            ).execute()
        self.spend, self.max_budget = get_spend(self.oncue_key)
        docs = (
            admin.table("documents")
            .select("id, filename, status, created_at")
            .eq("user_id", self.user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )
        self.docs = docs or []

    def mark_downloaded(self):
        self.ck_downloaded = True

    def mark_opened_app(self):
        self.ck_opened_app = True

    async def save_preferences(self, form_data: dict):
        self.preferences = form_data["preferences"]
        admin_client().table("profiles").update({"preferences": self.preferences}).eq(
            "id", self.user_id
        ).execute()
