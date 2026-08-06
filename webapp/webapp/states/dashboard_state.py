"""Dashboard state: OnCUE key + credit meter, reference documents,
preferences, and the onboarding checklist. All Supabase/LiteLLM calls are
thin pass-throughs to webapp.services.* — this class only orchestrates."""
from __future__ import annotations

import os
from urllib.parse import quote

import reflex as rx

from webapp.services.documents import embed, rag_url
from webapp.services.litellm import get_spend, mint_key
from webapp.services.supabase import admin_client
from webapp.states.auth_state import AuthState

FREE_DOC_LIMIT = 1


class DashboardState(AuthState):
    tier: str = "free"
    oncue_key: str = ""
    spend: float = 0.0
    max_budget: float = 0.0
    persona: str = ""
    preferences: str = ""
    docs: list[dict] = []
    site_url: str = ""
    rag_url_value: str = ""
    backend_url: str = ""
    session_count: int = 0
    trial_used: bool = False
    search_query: str = ""
    search_results: list[str] = []
    search_error: str = ""
    searching: bool = False
    copy_msg: str = "Copy"
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
    def trial_remaining(self) -> int:
        is_trial = (self.tier == "free" and not self.trial_used) or self.tier == "trial"
        if not is_trial:
            return 0
        return max(0, 1 - self.session_count)

    @rx.var
    def deep_link(self) -> str:
        if not self.oncue_key:
            return "#"
        parts = [f"token={quote(self.oncue_key, safe='')}"]
        if self.site_url:
            parts.append(f"web={quote(self.site_url, safe='')}")
        if self.rag_url_value:
            parts.append(f"rag={quote(self.rag_url_value, safe='')}")
        if self.backend_url:
            parts.append(f"backend={quote(self.backend_url, safe='')}")
        return f"oncue://connect?{'&'.join(parts)}"

    @rx.var
    def spend_label(self) -> str:
        return f"${self.spend:.3f} of ${self.max_budget:.2f} used this month"

    def _load_connect_urls(self) -> None:
        self.site_url = os.environ.get("SITE_URL", "").rstrip("/")
        self.rag_url_value = rag_url()
        self.backend_url = os.environ.get("LITELLM_URL", "").rstrip("/")

    async def load_dashboard(self):
        if not self.is_logged_in:
            yield rx.redirect("/login")
            return
        self._load_connect_urls()
        admin = admin_client()
        profile = (
            admin.table("profiles")
            .select(
                "tier, litellm_key, persona, preferences, session_count, trial_used"
            )
            .eq("id", self.user_id)
            .maybe_single()
            .execute()
            .data
            or {}
        )
        self.tier = profile.get("tier", "free")
        self.persona = profile.get("persona") or ""
        self.preferences = profile.get("preferences") or ""
        self.session_count = int(profile.get("session_count") or 0)
        self.trial_used = bool(profile.get("trial_used"))
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

    def copy_key(self):
        self.copy_msg = "Copied"

    def reset_copy_msg(self):
        self.copy_msg = "Copy"

    async def save_preferences(self, form_data: dict):
        self.preferences = form_data["preferences"]
        admin_client().table("profiles").update({"preferences": self.preferences}).eq(
            "id", self.user_id
        ).execute()

    async def search_documents(self):
        query = self.search_query.strip()
        if not query:
            return
        self.searching = True
        self.search_error = ""
        self.search_results = []
        yield
        try:
            vectors = embed([query])
            if not vectors:
                self.search_results = []
                return
            result = (
                admin_client()
                .rpc(
                    "match_doc_chunks",
                    {
                        "p_user_id": self.user_id,
                        "query_embedding": vectors[0],
                        "match_count": 5,
                    },
                )
                .execute()
            )
            rows = result.data or []
            self.search_results = [row["content"] for row in rows]
        except Exception as exc:  # noqa: BLE001
            self.search_error = str(exc)
        finally:
            self.searching = False

    async def delete_document(self, document_id: str):
        admin = admin_client()
        row = (
            admin.table("documents")
            .select("storage_path")
            .eq("id", document_id)
            .eq("user_id", self.user_id)
            .maybe_single()
            .execute()
            .data
        )
        if not row:
            return
        admin.table("doc_chunks").delete().eq("document_id", document_id).eq(
            "user_id", self.user_id
        ).execute()
        try:
            admin.storage.from_("documents").remove([row["storage_path"]])
        except Exception:  # noqa: BLE001 — storage cleanup is best-effort
            pass
        admin.table("documents").delete().eq("id", document_id).eq(
            "user_id", self.user_id
        ).execute()
        await self.load_dashboard()
