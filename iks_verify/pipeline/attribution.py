import re

from rapidfuzz import fuzz, process

from iks_verify.ingest.normalize import normalize_devanagari
from iks_verify.schemas import AttributionFlag, Verse


def normalize_citation_id(value: str) -> str:
    """Map common corpus-name spellings to the canonical text identifiers."""
    cleaned = " ".join(value.replace("\u202f", " ").split())
    cleaned = re.sub(r"^(?:gita|गीता|गिता|भगवद्गीता)\s+", "Gita ", cleaned, flags=re.I)
    cleaned = re.sub(
        r"^(?:yoga\s*sutras?|योग\s*सूत्र(?:ाणि)?|योगसूत्र(?:ाणि)?)\s+",
        "YogaSutras ",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"^(?:GITA)\s+", "Gita ", cleaned)
    return cleaned


def parse_verse_id(value: str) -> tuple[str, str, str] | None:
    match = re.fullmatch(r"\s*([\w-]+)\s+(\d+)\.(\d+)\s*", normalize_citation_id(value))
    return match.groups() if match else None


def check_attributions(
    answer: str,
    corpus: list[Verse],
    threshold: int = 82,
    question: str = "",
) -> list[AttributionFlag]:
    flags: list[AttributionFlag] = []
    canonical_ids = {verse.verse_id: normalize_citation_id(verse.verse_id) for verse in corpus}
    by_id = {
        canonical.casefold(): verse
        for verse in corpus
        for canonical in [canonical_ids[verse.verse_id]]
    }
    citations = re.findall(r"\[([^\]]+)\]", answer)
    # Questions such as “Quote Gita 19.5” are explicit attributions too,
    # even if the model wisely declines to repeat the bad citation.
    citations += re.findall(r"\b(?:Gita|YogaSutras|Yoga Sutras)\s+\d+\.\d+\b", question, flags=re.I)
    citations = list(dict.fromkeys(citations))
    for cited in citations:
        canonical_cited = normalize_citation_id(cited)
        if canonical_cited.casefold() not in by_id:
            closest = process.extractOne(canonical_cited, list(canonical_ids.values()), scorer=fuzz.ratio)
            flags.append(AttributionFlag(kind="FABRICATED_CITATION", cited=cited, message="Cited verse does not exist in this corpus.", closest_verse_id=closest[0] if closest else None))
    quoted = list(dict.fromkeys(re.findall(r"[“\"]([^”\"]{6,})[”\"]", f"{question}\n{answer}")))
    seen_normalized_quotes: set[str] = set()
    for quote in quoted:
        normalized = normalize_devanagari(quote)
        if not any("\u0900" <= char <= "\u097f" for char in normalized):
            continue
        # The model can repeat a quotation from the question using different
        # whitespace. It is one attribution claim, so emit one flag.
        if normalized in seen_normalized_quotes:
            continue
        seen_normalized_quotes.add(normalized)
        choices = {canonical_ids[verse.verse_id]: normalize_devanagari(verse.sanskrit_devanagari) for verse in corpus}
        closest = process.extractOne(normalized, choices, scorer=fuzz.ratio, processor=None)
        if not closest or closest[1] < threshold:
            closest_id = closest[2] if closest else None
            verse = next((item for item in corpus if item.verse_id == closest_id), None)
            flags.append(AttributionFlag(kind="FABRICATED" if not closest else "MISQUOTE", cited="Sanskrit quote", message="Quoted Sanskrit does not match the corpus.", closest_verse_id=closest_id, quoted_text=quote, actual_text=verse.sanskrit_devanagari if verse else None))
    return flags
