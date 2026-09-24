"""Interview & Meeting Mode — teleprompter-style session for mocks and standups."""

from __future__ import annotations

import re

from oncue.meeting_memory import format_for_prompt

INTERVIEW_CONFIRMATION = (
    "Interview & Meeting Mode locked. Teleprompter active. Context synced."
)

TELEPROMPTER_INSTRUCTIONS = """You are the user's personal teleprompter for a live interview or standup.
Voice and style:
- Sound like a natural human in conversation: contractions, occasional fillers ("uh", "so", "yeah"), short pauses, warm professional tone — never robotic or corporate.
- Keep answers concise enough to read aloud unless they asked for depth.

Question vs statement:
- If the input is clearly a QUESTION (ends with "?", or starts with can/could/would/what/how/why/when/who/do/does/did/is/are/will, etc.), answer directly and helpfully right away.
- If it is only a neutral STATEMENT with no implied request (e.g. "okay", "got it", "mm-hmm"), reply with at most one brief acknowledging line — do not lecture.
- If it is a statement that implies a problem or needs help (stuck, blocked, again, struggling, deployment, deadline), respond with empathy and practical next steps even without a question mark.

Coding / technical:
- For coding questions (write code, debug, fix, explain snippet, etc.): calm step-by-step tone, clean markdown code blocks, line-by-line explanation like pair programming, mention one alternative when useful.

Standup / continuity:
- Use the meeting memory below when relevant. Reference prior decisions naturally ("remember last time we said…"). Do not say you don't remember if memory contains related facts — synthesize from it honestly.
"""

_LOCK_PATTERNS = (
    re.compile(r"interview\s*(?:&|and)\s*meeting\s*mode", re.I),
    re.compile(r"switch\s+to\s+interview", re.I),
    re.compile(r"teleprompter\s+(?:mode|active)", re.I),
    re.compile(r"mock\s+interview\s+mode", re.I),
)

_UNLOCK_PATTERNS = (
    re.compile(r"exit\s+interview", re.I),
    re.compile(r"disable\s+interview", re.I),
    re.compile(r"end\s+interview\s+mode", re.I),
)

_QUESTION_START = re.compile(
    r"^\s*(?:can|could|would|should|what|which|who|whom|whose|when|where|why|how|"
    r"do|does|did|is|are|was|were|will|shall|may|might|have|has|had)\b",
    re.I,
)

_HELP_STATEMENT = re.compile(
    r"\b(stuck|blocked|blocker|again|struggling|help|issue|problem|broken|"
    r"deployment|pipeline|deadline|priority|remind me)\b",
    re.I,
)

_FILLER_ONLY = re.compile(
    r"^\s*(?:ok(?:ay)?|yeah|yep|yup|mm-?hmm|uh-?huh|right|sure|thanks|thank you|"
    r"cool|nice|got it|sounds good)[\s.!]*$",
    re.I,
)


class InterviewSession:
    def __init__(self) -> None:
        self.enabled = False
        self._last_question = ""

    def lock(self) -> str:
        self.enabled = True
        return INTERVIEW_CONFIRMATION

    def unlock(self) -> None:
        self.enabled = False

    def wants_lock(self, text: str) -> bool:
        t = text.strip()
        if not t or any(p.search(t) for p in _UNLOCK_PATTERNS):
            return False
        return any(p.search(t) for p in _LOCK_PATTERNS)

    def wants_unlock(self, text: str) -> bool:
        return any(p.search(text) for p in _UNLOCK_PATTERNS)

    def is_question(self, text: str) -> bool:
        t = text.strip()
        if not t:
            return False
        if t.endswith("?"):
            return True
        return bool(_QUESTION_START.match(t))

    def should_invoke_agent(self, text: str) -> bool:
        """Skip the LLM for pure filler acknowledgments in interview mode."""
        t = text.strip()
        if not t:
            return False
        if self.is_question(t):
            return True
        if _HELP_STATEMENT.search(t):
            return True
        if _FILLER_ONLY.match(t):
            return False
        if len(t) < 20 and not self.is_question(t):
            return False
        return True

    def filler_acknowledgment(self) -> str:
        return "Yeah — I'm with you. Go on when you're ready."

    def enrich_question(self, question: str) -> str:
        if not self.enabled:
            return question
        self._last_question = question.strip()
        memory = format_for_prompt()
        parts = [TELEPROMPTER_INSTRUCTIONS]
        if memory:
            parts.append("\n--- Meeting memory ---\n")
            parts.append(memory)
        parts.append("\n--- User (live) ---\n")
        parts.append(question)
        return "\n".join(parts)

    @property
    def last_question(self) -> str:
        return self._last_question
