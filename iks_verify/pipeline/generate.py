from iks_verify.llm.base import LLM
from iks_verify.schemas import Passage


async def grounded_answer(question: str, passages: list[Passage], llm: LLM) -> str:
    if not passages or passages[0].score <= 0:
        return "The provided texts do not contain enough information to answer this question."
    evidence = "\n".join(
        f"[{p.verse_id}] TRANSLATION: {p.english_translation}" for p in passages
    )
    prompt = (
        "Answer only from EVIDENCE. Cite every factual statement in the exact [Text chapter.verse] "
        "form. If evidence is insufficient, state that the provided texts do not contain enough information.\n"
        f"QUESTION: {question}\nEVIDENCE:\n{evidence}"
    )
    return await llm.complete(prompt)
