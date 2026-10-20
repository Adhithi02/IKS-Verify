"""Validate a JSONL corpus supplied by a public-domain source."""
import json
from collections import Counter
from pathlib import Path

from iks_verify.schemas import Verse

GITA_700 = {
    "1": 47, "2": 72, "3": 43, "4": 42, "5": 29, "6": 47, "7": 30, "8": 28,
    "9": 34, "10": 42, "11": 55, "12": 20, "13": 34, "14": 27, "15": 20, "16": 24,
    "17": 28, "18": 78,
}
EXPECTED = {
    "Gita": GITA_700,
    "YogaSutras": {"1": 51, "2": 55, "3": 55, "4": 34},
}


def load_verses(path: Path) -> list[Verse]:
    verses = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            verses.append(Verse.model_validate(json.loads(line)))
    return verses


def validate_corpus(path: Path) -> int:
    verses = load_verses(path)
    if any("FIXTURE_ONLY" in v.license or "FIXTURE_ONLY" in v.source for v in verses):
        raise ValueError("Production corpus still contains FIXTURE_ONLY records")
    print("text_id      n  expected  by-chapter (have/want)  status")
    failed = False
    by_text: dict[str, list[Verse]] = {}
    for verse in verses:
        by_text.setdefault(verse.text_id, []).append(verse)
    for text_id, expected in EXPECTED.items():
        subset = by_text.get(text_id, [])
        counts = Counter(v.chapter for v in subset)
        ok = dict(counts) == expected and len(subset) == sum(expected.values())
        detail = " ".join(f"{ch}:{counts.get(ch, 0)}/{n}" for ch, n in expected.items())
        print(f"{text_id:12} {len(subset):3} {sum(expected.values()):8}  {detail}  {'OK' if ok else 'FAIL'}")
        failed = failed or not ok
    if failed:
        raise SystemExit("corpus validation failed")
    return len(verses)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(f"Validated {validate_corpus(args.path)} verses")
