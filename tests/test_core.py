from pathlib import Path

from iks_verify.config import Settings
from iks_verify.index.hybrid import HybridRetriever
from iks_verify.ingest.normalize import normalize_devanagari
from iks_verify.llm.base import LLM, FallbackLLM
from iks_verify.llm.ratelimit import RateLimiter, with_backoff
from iks_verify.pipeline.attribution import (
    check_attributions,
    normalize_citation_id,
    parse_verse_id,
)
from iks_verify.pipeline.run import VerificationPipeline
from tests.helpers import run_immediately

FIXTURE = Path("tests/fixtures/corpus.jsonl")


def _settings(**kwargs) -> Settings:
    values = {"llm_provider": "mock", "corpus_path": FIXTURE, "embedding_model": "disabled"}
    values.update(kwargs)
    return Settings(**values)


def test_normalize_devanagari():
    assert normalize_devanagari("योगः ॥ २") == "योगः"


def test_parse_verse_id():
    assert parse_verse_id("Gita 2.47") == ("Gita", "2", "47")
    assert parse_verse_id("wrong") is None
    assert normalize_citation_id("गिता 2.47") == "Gita 2.47"
    assert normalize_citation_id("गीता 2.47") == "Gita 2.47"
    assert normalize_citation_id("योग सूत्र 1.2") == "YogaSutras 1.2"


def test_attribution_checks_fixture():
    retriever = HybridRetriever.from_jsonl(FIXTURE)
    flags = check_attributions("This is [Gita 99.99]", retriever.verses)
    assert flags[0].kind == "FABRICATED_CITATION"
    assert not check_attributions("[Gita 2.47]", retriever.verses)
    assert not check_attributions("[गिता 2.47]", retriever.verses)
    assert check_attributions("[Gita 19.5]", retriever.verses)[0].closest_verse_id == "Gita 2.47"


def test_retrieval():
    passage = HybridRetriever.from_jsonl(FIXTURE).retrieve("action fruits", 1)[0]
    assert passage.verse_id == "Gita 2.47"


def test_full_mock_pipeline(tmp_path):
    answer = run_immediately(
        VerificationPipeline(_settings(llm_cache_dir=tmp_path)).ask(
            "What does the Gita say about action and fruits?"
        )
    )
    assert answer.retrieved_passages
    assert answer.claims
    assert answer.claims[0].verdict is not None
    assert len(answer.claims) >= 2


def test_rate_limiter_releases_window_with_fake_clock():
    class FakeTime:
        value = 0.0

        def now(self) -> float:
            return self.value

        async def sleep(self, seconds: float) -> None:
            self.value += seconds

    fake = FakeTime()
    limiter = RateLimiter(1, 10, clock=fake.now, sleep=fake.sleep)

    async def scenario() -> None:
        await limiter.acquire(5)
        await limiter.acquire(5)

    run_immediately(scenario())
    assert fake.value == 60.0
    assert len(limiter.events) == 1


def test_rate_limiter_rejects_request_larger_than_budget():
    limiter = RateLimiter(1, 10)
    try:
        run_immediately(limiter.acquire(11))
    except ValueError as error:
        assert "exceeds" in str(error)
    else:
        raise AssertionError("Expected token budget validation")


def test_429_backoff_retries_without_real_sleep():
    attempts = 0
    delays: list[float] = []

    async def call() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("HTTP 429")
        return "ok"

    async def sleep(delay: float) -> None:
        delays.append(delay)

    assert run_immediately(with_backoff(call, sleep=sleep, jitter=lambda: 0)) == "ok"
    assert delays == [1, 2]


def test_provider_fallback_uses_secondary_client(tmp_path):
    class FakeLLM(LLM):
        def __init__(self, settings: Settings, result: str | Exception) -> None:
            super().__init__(settings)
            self.result = result

        async def _complete(self, prompt: str, model: str, temperature: float) -> str:
            if isinstance(self.result, Exception):
                raise self.result
            return self.result

    settings = _settings(llm_cache_dir=tmp_path)
    primary = FakeLLM(settings, RuntimeError("provider unavailable"))
    fallback = FakeLLM(settings, "fallback answer")
    assert run_immediately(FallbackLLM(primary, fallback).complete("unique prompt")) == "fallback answer"
