from collections.abc import AsyncGenerator

from iks_verify.config import Settings, get_settings
from iks_verify.index.hybrid import HybridRetriever
from iks_verify.llm.base import LLM, get_llm
from iks_verify.pipeline.attribution import check_attributions
from iks_verify.pipeline.claims import extract_claims
from iks_verify.pipeline.generate import grounded_answer
from iks_verify.pipeline.verify import verify_claims
from iks_verify.schemas import VerifiedAnswer


class VerificationPipeline:
    def __init__(self, settings: Settings | None = None, llm: LLM | None = None) -> None:
        self.settings = settings or get_settings()
        self.llm = llm or get_llm(self.settings)
        self.retriever = HybridRetriever.from_jsonl(
            self.settings.corpus_path,
            embedding_model=self.settings.embedding_model,
            index_dir=self.settings.index_dir,
        )

    async def events(self, question: str, system: str = "verify") -> AsyncGenerator[dict, None]:
        yield {"stage": "retrieving"}
        passages = self.retriever.retrieve(question)
        yield {"stage": "generating"}
        if system == "plain":
            answer = await self.llm.complete(question)
        else:
            answer = await grounded_answer(question, passages, self.llm)
        claims = []
        flags = []
        if system not in {"rag"}:
            yield {"stage": "extracting_claims"}
            claims = await extract_claims(answer, [p.verse_id for p in passages], self.llm)
            yield {"stage": "verifying"}
            claims = await verify_claims(claims, passages, self.llm)
            yield {"stage": "checking_attributions"}
            flags = check_attributions(
                answer,
                self.retriever.verses,
                self.settings.quote_match_threshold,
                question=question,
            )
        supported = sum(claim.verdict and claim.verdict.value == "SUPPORTED" for claim in claims)
        contradicted = sum(claim.verdict and claim.verdict.value == "CONTRADICTED" for claim in claims)
        unverifiable = sum(claim.verdict and claim.verdict.value == "UNVERIFIABLE" for claim in claims)
        score = supported / len(claims) if claims else 0.0
        score = max(0.0, score - min(0.5, len(flags) * 0.2))
        abstained = "do not contain enough information" in answer.lower()
        result = VerifiedAnswer(
            answer=answer,
            claims=claims,
            attribution_flags=flags,
            retrieved_passages=passages,
            trust_score=round(score, 2),
            model_name=self.settings.llm_model or "mock",
            judge_model_name=self.settings.judge_model or "mock",
            system=system,
            abstained=abstained,
        )
        yield {
            "stage": "done",
            "result": result.model_dump(mode="json"),
            "verdict_counts": {
                "supported": supported,
                "contradicted": contradicted,
                "unverifiable": unverifiable,
            },
        }

    async def ask(self, question: str, system: str = "verify") -> VerifiedAnswer:
        result = None
        async for event in self.events(question, system):
            if event["stage"] == "done":
                result = VerifiedAnswer.model_validate(event["result"])
        assert result is not None
        return result
