from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_provider: str = "mock"
    llm_model: str = ""
    judge_model: str = ""
    llm_fallback_provider: str | None = None
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    openrouter_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_requests_per_minute: int = 20
    llm_tokens_per_minute: int = 10_000
    llm_daily_request_budget: int = 1_000
    llm_cache_dir: Path = Path(".cache/llm")
    embedding_model: str = "BAAI/bge-m3"
    embedding_fallback_model: str = "intfloat/multilingual-e5-small"
    quote_match_threshold: int = 82
    corpus_path: Path = Path("data/processed/corpus.jsonl")
    index_dir: Path = Path("data/processed")
    selfcheck_samples: int = 3

    @property
    def is_mock(self) -> bool:
        return self.llm_provider == "mock" or not self.api_key_for(self.llm_provider)

    def api_key_for(self, provider: str) -> str | None:
        return getattr(self, f"{provider}_api_key", None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
