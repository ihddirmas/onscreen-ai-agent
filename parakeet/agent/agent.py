"""LangGraph ReAct agent: model + tools + memory + confirmation interrupts."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from parakeet.agent.router import get_model
from parakeet.agent.tools import tools_for
from parakeet.config import get_config


def _has_image(m) -> bool:
    return (
        isinstance(m, HumanMessage)
        and isinstance(m.content, list)
        and any(isinstance(b, dict) and b.get("type") == "image_url" for b in m.content)
    )


def _text_only(m: HumanMessage) -> HumanMessage:
    text = " ".join(
        b.get("text", "")
        for b in m.content
        if isinstance(b, dict) and b.get("type") == "text"
    )
    return HumanMessage(content=f"{text}\n[screenshot omitted — already analyzed]", id=m.id)


def _strip_old_images(state):
    """Token-budget guard (Groq free tier is 8k tokens/min): send a screenshot
    to the model only on the FIRST model call of the turn it belongs to.
    Older turns' screenshots and this turn's screenshot on post-tool calls are
    replaced with a text placeholder; stored history is left untouched."""
    msgs = list(state["messages"])
    image_indices = [i for i, m in enumerate(msgs) if _has_image(m)]
    if not image_indices:
        return {"llm_input_messages": msgs}
    last = image_indices[-1]
    # if anything (AI/tool messages) follows the latest screenshot, the model
    # has already seen it this turn — drop it on this call too
    keep_last = last == len(msgs) - 1
    out = []
    for i, m in enumerate(msgs):
        if _has_image(m) and not (keep_last and i == last):
            m = _text_only(m)
        out.append(m)
    return {"llm_input_messages": out}

SYSTEM = (
    "You are Parakeet, an on-screen desktop assistant. When a screenshot is "
    "attached to the user's message you can see their screen; without one, "
    "answer as a normal chat assistant. Answer directly when you can, but if "
    "the question depends on current or real-world information (news, prices, "
    "recent events, people, releases) or you are unsure, call web_search first "
    "and base your answer on the results — do not guess. web_search results are "
    "usually enough on their own: answer from them directly and do NOT call "
    "browse afterwards unless the user explicitly needs the full text of one "
    "specific page. "
    "Use web_search for facts; open_website/google_search/"
    "youtube_search to open things in the browser; browse to read a page; "
    "launch_app to open apps; open_file/find_files/search_documents to work "
    "with local files (limited to allowed folders). "
    "The user may have uploaded reference material (resume, notes, study plans). "
    "Whenever their own background, projects, or notes could improve the answer, "
    "call search_my_documents first and use what it returns to give a better, "
    "more personal answer — silently. Do NOT say 'according to your document' or "
    "cite the source; just answer well. "
    "Never claim you performed an action a tool didn't confirm. Keep answers "
    "concise — they render on a small overlay."
)


def _user_profile() -> str:
    """Fetch the user's persona + preferences from the website (hosted mode) to
    personalize every answer. Best-effort — returns '' if unavailable."""
    cfg = get_config()
    if not cfg.web_url or not cfg.parakeet_token:
        return ""
    try:
        import json
        import urllib.request

        req = urllib.request.Request(
            f"{cfg.web_url.rstrip('/')}/api/me/profile",
            headers={"Authorization": f"Bearer {cfg.parakeet_token}"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return ""
    persona = (data.get("persona") or "").strip()
    prefs = (data.get("preferences") or "").strip()
    if not persona and not prefs:
        return ""
    parts = ["\n\nAbout this user (personalize your answers accordingly):"]
    if persona:
        parts.append(f" {persona}")
    if prefs:
        parts.append(f" Their stated preferences: {prefs} Follow these preferences "
                     f"(e.g. preferred programming language for code answers).")
    return "".join(parts)


def build_agent(provider: str | None = None, allow_system: bool = True):
    """Build (or rebuild) the ReAct agent. When allow_system is False the agent
    gets only information tools — it can't open apps/files/browser or read
    local files (the overlay's System-actions toggle)."""
    return create_react_agent(
        get_model(provider),
        tools=tools_for(allow_system),
        checkpointer=MemorySaver(),
        prompt=SYSTEM + _user_profile(),
        pre_model_hook=_strip_old_images,
    )
