from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from iks_verify.pipeline.run import VerificationPipeline
from iks_verify.schemas import VerifiedAnswer

router = APIRouter()
pipeline = VerificationPipeline()

ALLOWED = {"plain", "rag", "verify", "selfcheck"}


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    system: str = "verify"


@router.post("/ask", response_model=VerifiedAnswer)
async def ask(request: AskRequest) -> VerifiedAnswer:
    if request.system not in ALLOWED:
        raise HTTPException(422, "system must be plain, rag, verify, or selfcheck")
    try:
        if request.system == "selfcheck":
            from iks_verify.baselines.selfcheck import run as run_selfcheck

            return await run_selfcheck(request.question, pipeline)
        return await pipeline.ask(request.question, request.system)
    except Exception as error:
        if "429" in str(error) or "quota" in str(error).lower():
            retry = pipeline.llm.last_retry_after or "60"
            return JSONResponse(  # type: ignore[return-value]
                {"error": "rate_limited", "retry_after": retry},
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
        raise


@router.post("/compare")
async def compare(request: AskRequest) -> dict[str, VerifiedAnswer]:
    return {system: await pipeline.ask(request.question, system) for system in ("plain", "rag", "verify")}


@router.get("/verse/{text_id}/{chapter}/{verse}")
async def verse(text_id: str, chapter: str, verse: str) -> dict:
    match = next(
        (
            item
            for item in pipeline.retriever.verses
            if (item.text_id, item.chapter, item.verse) == (text_id, chapter, verse)
        ),
        None,
    )
    if not match:
        raise HTTPException(404, "Verse not found")
    return match.model_dump()


@router.get("/examples")
async def examples() -> list[dict[str, str]]:
    return [
        {"label": "Action and results", "question": "What does the Gita say about action and its fruits?"},
        {"label": "Yoga definition", "question": "How does the Yoga Sutra define yoga?"},
        {"label": "Trap: fake citation", "question": "What does Gita 99.99 say about quantum physics?"},
    ]


@router.get("/health")
async def health() -> dict[str, str | bool | int]:
    settings = pipeline.settings
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "mock_mode": settings.is_mock,
        "api_calls": pipeline.llm.calls,
    }
