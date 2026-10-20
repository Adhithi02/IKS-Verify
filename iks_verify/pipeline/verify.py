import json

from iks_verify.llm.base import LLM
from iks_verify.pipeline.claims import parse_json
from iks_verify.schemas import Claim, Passage, Verdict


async def verify_claims(claims: list[Claim], passages: list[Passage], llm: LLM) -> list[Claim]:
    if not claims:
        return []
    evidence = "\n".join(f"[{p.verse_id}] {p.english_translation}" for p in passages)
    payload = json.dumps([{"text": claim.text, "citations": claim.citations} for claim in claims])
    prompt = (
        "VERIFY_CLAIMS\nFor each claim return JSON array in same order with verdict (SUPPORTED, "
        "CONTRADICTED, UNVERIFIABLE), supporting_verse_ids, rationale.\n"
        f"CLAIMS: {payload}\nEVIDENCE:\n{evidence}"
    )
    try:
        result = parse_json(await llm.complete(prompt, llm.settings.judge_model))
    except (json.JSONDecodeError, ValueError, TypeError):
        result = []
    for index, claim in enumerate(claims):
        item = result[index] if index < len(result) else {}
        try:
            claim.verdict = Verdict(item.get("verdict", "UNVERIFIABLE"))
        except ValueError:
            claim.verdict = Verdict.UNVERIFIABLE
        claim.supporting_verse_ids = item.get("supporting_verse_ids", [])
        claim.rationale = item.get("rationale", "The verifier could not establish this claim.")
    return claims
