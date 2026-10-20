from abc import ABC, abstractmethod

from iks_verify.config import Settings, get_settings
from iks_verify.llm.cache import DiskCache
from iks_verify.llm.ratelimit import RateLimiter, with_backoff


class LLM(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.cache = DiskCache(settings.llm_cache_dir)
        self.limiter = RateLimiter(settings.llm_requests_per_minute, settings.llm_tokens_per_minute)
        self.calls = 0
        self.last_remaining_requests: str | None = None
        self.last_remaining_tokens: str | None = None
        self.last_retry_after: str | None = None

    def _store_rate_headers(self, headers) -> None:
        mapping = {k.lower(): v for k, v in headers.items()}
        self.last_remaining_requests = mapping.get("x-ratelimit-remaining-requests") or mapping.get(
            "x-ratelimit-remaining"
        )
        self.last_remaining_tokens = mapping.get("x-ratelimit-remaining-tokens")
        self.last_retry_after = mapping.get("retry-after")

    def budget_line(self) -> str:
        remaining_daily = max(0, self.settings.llm_daily_request_budget - self.calls)
        parts = [f"API calls: {self.calls}", f"est. remaining daily budget: {remaining_daily}"]
        if self.last_remaining_requests:
            parts.append(f"provider remaining-requests: {self.last_remaining_requests}")
        if self.last_remaining_tokens:
            parts.append(f"provider remaining-tokens: {self.last_remaining_tokens}")
        if self.last_retry_after:
            parts.append(f"retry-after: {self.last_retry_after}")
        return " | ".join(parts)

    @abstractmethod
    async def _complete(self, prompt: str, model: str, temperature: float) -> str: ...

    async def complete(self, prompt: str, model: str | None = None, temperature: float = 0) -> str:
        model = model or self.settings.llm_model
        cache_key = f"{model}|{temperature}|{prompt}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        await self.limiter.acquire(max(1, len(prompt) // 4))
        self.calls += 1
        result = await with_backoff(lambda: self._complete(prompt, model, temperature))
        self.cache.set(cache_key, result)
        return result


class FallbackLLM(LLM):
    def __init__(self, primary: LLM, fallback: LLM) -> None:
        self.primary = primary
        self.fallback = fallback
        super().__init__(primary.settings)

    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        raise NotImplementedError

    async def complete(self, prompt: str, model: str | None = None, temperature: float = 0) -> str:
        try:
            return await self.primary.complete(prompt, model, temperature)
        except Exception:
            return await self.fallback.complete(prompt, model, temperature)

    @property
    def calls(self) -> int:
        return self.primary.calls + self.fallback.calls

    @calls.setter
    def calls(self, value: int) -> None:
        return


def _provider_llm(settings: Settings) -> LLM:
    if settings.is_mock:
        from iks_verify.llm.mock import MockLLM

        return MockLLM(settings)
    clients = {
        "groq": "groq_client",
        "gemini": "gemini_client",
        "openrouter": "openrouter_client",
        "openai": "openai_client",
        "anthropic": "anthropic_client",
    }
    module_name = clients.get(settings.llm_provider)
    if not module_name:
        raise ValueError(f"Unsupported provider: {settings.llm_provider}")
    module = __import__(f"iks_verify.llm.{module_name}", fromlist=["ProviderLLM"])
    return module.ProviderLLM(settings)


def get_llm(settings: Settings | None = None) -> LLM:
    settings = settings or get_settings()
    primary = _provider_llm(settings)
    if not settings.llm_fallback_provider:
        return primary
    fallback_settings = settings.model_copy(update={"llm_provider": settings.llm_fallback_provider})
    return FallbackLLM(primary, _provider_llm(fallback_settings))
