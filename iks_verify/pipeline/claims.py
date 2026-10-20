import json
import re

from iks_verify.llm.base import LLM
from iks_verify.schemas import Claim

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I | re.M)
_TRAILING_COMMA = re.compile(r",\s*([\]}])")


def parse_json(value: str) -> object:
    text = value.strip()
    text = _FENCE.sub("", text).strip()
    match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.S)
    if match:
        text = match.group(1)
    text = _TRAILING_COMMA.sub(r"\1", text)
    return json.loads(text)


def _atomic_fallback(answer: str) -> list[Claim]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", answer) if part.strip()]
    claims: list[Claim] = []
    for part in parts:
        citations = re.findall(r"\[([^\]]+)\]", part)
        claims.append(Claim(text=part, citations=citations))
    return claims


async def extract_claims(answer: str, evidence_ids: list[str], llm: LLM) -> list[Claim]:
    prompt = (
        "EXTRACT_CLAIMS\nReturn a JSON array of atomic self-contained claims. Each object must have "
        "keys text (one fact) and citations (verse ids from evidence only). Split compound sentences.\n"
        f"ANSWER: {answer}\nEVIDENCE: {', '.join(f'[{item}]' for item in evidence_ids)}"
    )
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            raw = await llm.complete(
                prompt if attempt == 0 else prompt + "\nSTRICT: valid JSON array only, no prose.",
                llm.settings.judge_model,
            )
            parsed = parse_json(raw)
            if isinstance(parsed, dict):
                parsed = parsed.get("claims", [parsed])
            claims = [Claim.model_validate(item) for item in parsed]
            if claims:
                return claims
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            last_error = error
            continue
    _ = last_error
    return _atomic_fallback(answer) if answer else []
