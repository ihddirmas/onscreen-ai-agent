"""Unit tests for DashboardState.

DashboardState is a Reflex ``rx.State`` subclass, and Reflex refuses to
instantiate State classes directly in application code ("State classes
should not be instantiated directly in a Reflex app"). For unit testing
the orchestration logic in isolation (without booting a full Reflex app,
browser, or Supabase project), we use Reflex's own internal
``_reflex_internal_init=True`` escape hatch — this is the same knob Reflex
itself relies on to construct bare state instances outside a live app
context. It gives us a real, working state object (computed vars, cookie
fields, and async event handlers all behave normally) so we can verify the
state's business logic the same way the other service layers are tested:
by mocking `webapp.services.*` at the call site and asserting on state
transitions, without fighting Reflex's rendering machinery.
"""
from __future__ import annotations

import pytest

from webapp.states import dashboard_state as dashboard_state_module
from webapp.states.auth_state import AuthState
from webapp.states.dashboard_state import DashboardState


def _make_state(**overrides) -> DashboardState:
    # DashboardState inherits AuthState (access_token, user_id, ...), and
    # Reflex resolves inherited vars through `parent_state`. A standalone
    # `DashboardState(_reflex_internal_init=True)` has no parent, so setting
    # any inherited var raises. Build the real parent chain instead.
    root = AuthState(_reflex_internal_init=True)
    state = DashboardState(parent_state=root, _reflex_internal_init=True)
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


class _FakeResult:
    def __init__(self, data):
        self.data = data


class _FakeQuery:
    """Chainable stand-in for a supabase-py PostgREST query builder."""

    def __init__(self, table_name: str, table_data: dict, calls: list):
        self._table_name = table_name
        self._table_data = table_data
        self._calls = calls

    def select(self, *args, **kwargs):
        self._calls.append(("select", self._table_name, args, kwargs))
        return self

    def eq(self, *args, **kwargs):
        self._calls.append(("eq", self._table_name, args, kwargs))
        return self

    def order(self, *args, **kwargs):
        self._calls.append(("order", self._table_name, args, kwargs))
        return self

    def maybe_single(self):
        self._calls.append(("maybe_single", self._table_name))
        return self

    def single(self):
        self._calls.append(("single", self._table_name))
        return self

    def update(self, values):
        self._calls.append(("update", self._table_name, values))
        return self

    def insert(self, values):
        self._calls.append(("insert", self._table_name, values))
        return self

    def execute(self):
        return _FakeResult(self._table_data.get(self._table_name))


class _FakeAdminClient:
    def __init__(self, table_data: dict):
        self.table_data = table_data
        self.calls: list = []

    def table(self, name: str) -> _FakeQuery:
        return _FakeQuery(name, self.table_data, self.calls)


async def _drain(async_gen):
    """Run an async-generator event handler to completion, collecting yields."""
    events = []
    async for event in async_gen:
        events.append(event)
    return events


# --- computed vars -----------------------------------------------------


def test_credit_pct_is_zero_when_max_budget_not_positive():
    state = _make_state(spend=5.0, max_budget=0.0)
    assert state.credit_pct == 0.0


def test_credit_pct_computes_percentage():
    state = _make_state(spend=0.5, max_budget=1.0)
    assert state.credit_pct == 50.0


def test_credit_pct_caps_at_100():
    state = _make_state(spend=5.0, max_budget=1.0)
    assert state.credit_pct == 100.0


def test_has_ready_doc_false_when_no_docs():
    state = _make_state(docs=[])
    assert state.has_ready_doc is False


def test_has_ready_doc_false_when_no_doc_is_ready():
    state = _make_state(docs=[{"status": "processing"}, {"status": "error"}])
    assert state.has_ready_doc is False


def test_has_ready_doc_true_when_a_doc_is_ready():
    state = _make_state(docs=[{"status": "processing"}, {"status": "ready"}])
    assert state.has_ready_doc is True


def test_checklist_complete_requires_all_three_conditions():
    state = _make_state(ck_downloaded=True, ck_opened_app=True, docs=[])
    assert state.checklist_complete is False

    state.docs = [{"status": "ready"}]
    assert state.checklist_complete is True

    state.ck_downloaded = False
    assert state.checklist_complete is False


def test_deep_link_is_hash_without_a_key():
    state = _make_state(oncue_key="")
    assert state.deep_link == "#"


def test_deep_link_embeds_token_web_rag_and_backend():
    state = _make_state(
        oncue_key="sk-user-abc",
        site_url="https://app.example.com",
        rag_url_value="https://db.example.com/functions/v1/rag",
        backend_url="https://litellm.example.com",
    )
    link = state.deep_link
    assert link.startswith("oncue://connect?")
    assert "token=sk-user-abc" in link
    assert "web=https%3A%2F%2Fapp.example.com" in link
    assert "rag=https%3A%2F%2Fdb.example.com%2Ffunctions%2Fv1%2Frag" in link
    assert "backend=https%3A%2F%2Flitellm.example.com" in link


def test_trial_remaining_for_unused_free_tier():
    state = _make_state(tier="free", trial_used=False, session_count=0)
    assert state.trial_remaining == 1


def test_trial_remaining_zero_after_session():
    state = _make_state(tier="free", trial_used=False, session_count=1)
    assert state.trial_remaining == 0


def test_trial_remaining_zero_for_pro():
    state = _make_state(tier="pro", trial_used=False, session_count=0)
    assert state.trial_remaining == 0


# --- simple mutators -----------------------------------------------------


def test_mark_downloaded_sets_the_checklist_cookie():
    state = _make_state(ck_downloaded=False)
    state.mark_downloaded()
    assert state.ck_downloaded is True


def test_mark_opened_app_sets_the_checklist_cookie():
    state = _make_state(ck_opened_app=False)
    state.mark_opened_app()
    assert state.ck_opened_app is True


# --- load_dashboard ------------------------------------------------------


@pytest.mark.asyncio
async def test_load_dashboard_redirects_when_not_logged_in(monkeypatch):
    def _fail_if_called(*args, **kwargs):
        raise AssertionError("admin_client should not be called when logged out")

    monkeypatch.setattr(dashboard_state_module, "admin_client", _fail_if_called)
    state = _make_state(access_token="")

    events = await _drain(state.load_dashboard())

    assert len(events) == 1


@pytest.mark.asyncio
async def test_load_dashboard_uses_existing_key_without_minting(monkeypatch):
    fake_admin = _FakeAdminClient(
        {
            "profiles": {
                "tier": "pro",
                "litellm_key": "sk-existing",
                "persona": "a backend engineer",
                "preferences": "be concise",
            },
            "documents": [{"id": "1", "filename": "notes.txt", "status": "ready"}],
        }
    )

    monkeypatch.setattr(dashboard_state_module, "admin_client", lambda: fake_admin)

    def _fail_mint(*args, **kwargs):
        raise AssertionError("mint_key should not be called when a key already exists")

    monkeypatch.setattr(dashboard_state_module, "mint_key", _fail_mint)
    monkeypatch.setattr(dashboard_state_module, "get_spend", lambda key: (0.42, 15.0))

    state = _make_state(access_token="tok", user_id="user-1")
    events = await _drain(state.load_dashboard())

    assert events == []
    assert state.tier == "pro"
    assert state.persona == "a backend engineer"
    assert state.preferences == "be concise"
    assert state.oncue_key == "sk-existing"
    assert state.spend == 0.42
    assert state.max_budget == 15.0
    assert state.docs == [{"id": "1", "filename": "notes.txt", "status": "ready"}]
    # No profile update should have been issued since nothing needed minting.
    assert not any(call[0] == "update" for call in fake_admin.calls)


@pytest.mark.asyncio
async def test_load_dashboard_mints_and_persists_key_when_missing(monkeypatch):
    fake_admin = _FakeAdminClient(
        {
            "profiles": {"tier": "free", "litellm_key": None, "persona": None, "preferences": None},
            "documents": [],
        }
    )

    monkeypatch.setattr(dashboard_state_module, "admin_client", lambda: fake_admin)

    minted = {}

    def _mint_key(user_id, tier):
        minted["user_id"] = user_id
        minted["tier"] = tier
        return "sk-freshly-minted"

    monkeypatch.setattr(dashboard_state_module, "mint_key", _mint_key)
    monkeypatch.setattr(dashboard_state_module, "get_spend", lambda key: (0.0, 1.0))

    state = _make_state(access_token="tok", user_id="user-2")
    await _drain(state.load_dashboard())

    assert minted == {"user_id": "user-2", "tier": "free"}
    assert state.oncue_key == "sk-freshly-minted"
    assert state.docs == []
    update_calls = [call for call in fake_admin.calls if call[0] == "update"]
    assert len(update_calls) == 1
    assert update_calls[0][2] == {"litellm_key": "sk-freshly-minted"}


@pytest.mark.asyncio
async def test_load_dashboard_defaults_missing_profile_fields(monkeypatch):
    fake_admin = _FakeAdminClient({"profiles": None, "documents": None})
    monkeypatch.setattr(dashboard_state_module, "admin_client", lambda: fake_admin)
    monkeypatch.setattr(dashboard_state_module, "mint_key", lambda user_id, tier: "sk-new")
    monkeypatch.setattr(dashboard_state_module, "get_spend", lambda key: (0.0, 0.0))

    state = _make_state(access_token="tok", user_id="user-3")
    await _drain(state.load_dashboard())

    assert state.tier == "free"
    assert state.persona == ""
    assert state.preferences == ""
    assert state.docs == []


# --- save_preferences ------------------------------------------------------


@pytest.mark.asyncio
async def test_save_preferences_updates_state_and_persists(monkeypatch):
    fake_admin = _FakeAdminClient({"profiles": {}})
    monkeypatch.setattr(dashboard_state_module, "admin_client", lambda: fake_admin)

    state = _make_state(user_id="user-1", preferences="")
    await state.save_preferences({"preferences": "answer tersely, show code first"})

    assert state.preferences == "answer tersely, show code first"
    update_calls = [call for call in fake_admin.calls if call[0] == "update"]
    assert len(update_calls) == 1
    assert update_calls[0][2] == {"preferences": "answer tersely, show code first"}
    eq_calls = [call for call in fake_admin.calls if call[0] == "eq"]
    assert eq_calls[-1][2] == ("id", "user-1")
