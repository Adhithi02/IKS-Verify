import re

from rapidfuzz import fuzz, process

from iks_verify.ingest.normalize import normalize_devanagari
from iks_verify.schemas import AttributionFlag, Verse


def parse_verse_id(value: str) -> tuple[str, str, str] | None:
    match = re.fullmatch(r"\s*([\w-]+)\s+(\d+)\.(\d+)\s*", value)
    return match.groups() if match else None


def check_attributions(answer: str, corpus: list[Verse], threshold: int = 82) -> list[AttributionFlag]:
    flags: list[AttributionFlag] = []
    by_id = {verse.verse_id.lower(): verse for verse in corpus}
    citations = re.findall(r"\[([^\]]+)\]", answer)
    for cited in citations:
        if cited.lower() not in by_id:
            closest = process.extractOne(cited, list(by_id), scorer=fuzz.ratio)
            flags.append(AttributionFlag(kind="FABRICATED_CITATION", cited=cited, message="Cited verse does not exist in this corpus.", closest_verse_id=closest[0] if closest else None))
    quoted = re.findall(r"[“\"]([^”\"]{6,})[”\"]", answer)
    for quote in quoted:
        normalized = normalize_devanagari(quote)
        if not any("\u0900" <= char <= "\u097f" for char in normalized):
            continue
        choices = {verse.verse_id: normalize_devanagari(verse.sanskrit_devanagari) for verse in corpus}
        closest = process.extractOne(normalized, choices, scorer=fuzz.ratio, processor=None)
        if not closest or closest[1] < threshold:
            verse = next((item for item in corpus if closest and item.verse_id == closest[0]), None)
            flags.append(AttributionFlag(kind="FABRICATED" if not closest else "MISQUOTE", cited="Sanskrit quote", message="Quoted Sanskrit does not match the corpus.", closest_verse_id=closest[0] if closest else None, quoted_text=quote, actual_text=verse.sanskrit_devanagari if verse else None))
    return flags
