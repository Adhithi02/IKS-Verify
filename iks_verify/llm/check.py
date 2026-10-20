"""List provider models, compare configured names, and make one tiny test call. Never print keys."""
from __future__ import annotations

import asyncio

import httpx

from iks_verify.config import Settings
from iks_verify.llm.base import get_llm
from iks_verify.runtime import configure_event_loop


def _key_status(value: str | None) -> str:
    return "set" if value else "missing"


async def list_models(settings: Settings) -> list[str]:
    provider = settings.llm_provider
    headers: dict[str, str] = {}
    url = ""
    if provider == "groq":
        url = "https://api.groq.com/openai/v1/models"
        if settings.groq_api_key:
            headers["Authorization"] = f"Bearer {settings.groq_api_key}"
    elif provider == "openai":
        url = "https://api.openai.com/v1/models"
        if settings.openai_api_key:
            headers["Authorization"] = f"Bearer {settings.openai_api_key}"
    elif provider == "openrouter":
        url = "https://openrouter.ai/api/v1/models"
        if settings.openrouter_api_key:
            headers["Authorization"] = f"Bearer {settings.openrouter_api_key}"
    elif provider == "gemini":
        if not settings.gemini_api_key:
            return []
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.gemini_api_key}"
    elif provider in {"mock", ""}:
        return ["mock"]
    elif provider == "anthropic":
        return []
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
    if provider == "gemini":
        return [item.get("name", "").split("/")[-1] for item in payload.get("models", [])]
    return [item.get("id", "") for item in payload.get("data", [])]


async def main() -> None:
    settings = Settings()
    print(f"provider: {settings.llm_provider}")
    print(f"LLM_MODEL: {settings.llm_model or '(unset)'}")
    print(f"JUDGE_MODEL: {settings.judge_model or '(unset)'}")
    print(f"API key: {_key_status(settings.api_key_for(settings.llm_provider))}")
    if settings.is_mock:
        print("mock mode: no remote /models call")
        llm = get_llm(settings)
        result = await llm.complete("Reply with the single word pong.")
        print(f"test call: {result[:120]!r}")
        print(llm.budget_line())
        return
    try:
        models = await list_models(settings)
    except Exception as error:
        print(f"models list FAILED: {error}")
        models = []
    print(f"available models ({len(models)}):")
    for name in models[:80]:
        print(f"  {name}")
    if len(models) > 80:
        print(f"  ... {len(models) - 80} more")
    for label, configured in (("LLM_MODEL", settings.llm_model), ("JUDGE_MODEL", settings.judge_model)):
        if not configured:
            print(f"{label} is empty — choose a name from the list above")
        elif models and configured not in models:
            print(f"WARNING: {label}={configured} is not in the provider list")
        elif models:
            print(f"{label} is present in the provider list")
    llm = get_llm(settings)
    try:
        result = await llm.complete("Reply with the single word pong.")
        print(f"test call: {result[:160]!r}")
        print(llm.budget_line())
    except Exception as error:
        print(f"test call FAILED: {error}")


if __name__ == "__main__":
    configure_event_loop()
    asyncio.run(main())
