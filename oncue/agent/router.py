"""Model router: one LangChain chat model per provider.

Providers:
  groq   — free tier for dev/testing (Llama 4 Scout: vision + tool calling)
  claude — production option (BYO ANTHROPIC_API_KEY)
  gpt    — production option (BYO OPENAI_API_KEY)
  gemini — production option (BYO GOOGLE_API_KEY)
  hosted — production default for end users: an OpenAI-compatible endpoint on
           OUR LiteLLM proxy, which holds the real provider keys server-side.
"""

from __future__ import annotations

import base64
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from oncue.config import get_config

PROVIDERS = ("groq", "claude", "gpt", "gemini", "hosted")


def get_model(name: str | None = None) -> BaseChatModel:
    cfg = get_config()
    name = name or cfg.provider
    if name == "groq":
        from langchain_groq import ChatGroq

        kwargs = {}
        # qwen/deepseek on Groq are reasoning models that emit <think> blocks;
        # have Groq strip them server-side so they don't render on the overlay.
        if "qwen" in cfg.groq_model or "deepseek" in cfg.groq_model:
            kwargs["reasoning_format"] = "hidden"
        # reasoning models consume output tokens thinking even when the
        # reasoning is hidden — give them room or answers truncate
        return ChatGroq(model=cfg.groq_model, max_tokens=4096, **kwargs)
    if name == "claude":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=cfg.claude_model, max_tokens=1024)
    if name == "gpt":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=cfg.gpt_model)
    if name == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Pass the key explicitly rather than via apply_env()/os.environ: the
        # SDK looks for GOOGLE_API_KEY by convention, and passing it directly
        # sidesteps any env-var-name mismatch.
        return ChatGoogleGenerativeAI(model=cfg.gemini_model, google_api_key=cfg.gemini_api_key)
    if name == "hosted":
        from langchain_openai import ChatOpenAI

        if not cfg.backend_url or not cfg.oncue_token:
            raise ValueError(
                "Hosted mode needs ONCUE_BACKEND_URL and ONCUE_TOKEN "
                "(open Settings and sign in with your license key)."
            )
        return ChatOpenAI(
            model=cfg.hosted_model,
            api_key=cfg.oncue_token,
            base_url=cfg.backend_url,
        )
    raise ValueError(f"unknown provider: {name}")


def build_message(instruction: str, screenshot_png: Optional[bytes]) -> HumanMessage:
    """User turn with the screenshot riding along as a data-URI image block."""
    content: list[dict] = [{"type": "text", "text": instruction}]
    if screenshot_png:
        mime = "image/png" if screenshot_png[:4] == b"\x89PNG" else "image/jpeg"
        b64 = base64.standard_b64encode(screenshot_png).decode()
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        )
    return HumanMessage(content=content)
