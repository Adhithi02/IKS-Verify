"""Download openly licensed / public-domain IKS texts. Never invent Sanskrit."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import httpx

from iks_verify.schemas import Verse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SOURCES_MD = ROOT / "data" / "SOURCES.md"
RETRIEVED = date.today().isoformat()
UA = {"User-Agent": "IKS-Verify/0.1 (research corpus ingest; local academic prototype)"}

GITA_700 = {
    "1": 47, "2": 72, "3": 43, "4": 42, "5": 29, "6": 47, "7": 30, "8": 28,
    "9": 34, "10": 42, "11": 55, "12": 20, "13": 34, "14": 27, "15": 20, "16": 24,
    "17": 28, "18": 78,
}
YOGA_195 = {"1": 51, "2": 55, "3": 55, "4": 34}
PROVENANCE: list[dict[str, str]] = []


def fetch(url: str, dest: Path | None = None) -> str:
    RAW.mkdir(parents=True, exist_ok=True)
    response = httpx.get(url, headers=UA, follow_redirects=True, timeout=90.0)
    response.raise_for_status()
    text = response.content.decode("utf-8")
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return text


def record(name: str, url: str, license_name: str, note: str) -> None:
    PROVENANCE.append({
        "name": name, "url": url, "license": license_name,
        "retrieved": RETRIEVED, "note": note,
    })


def strip_verse_numbers(sanskrit: str) -> str:
    sanskrit = re.sub(r"।।\s*\d+\s*[.।-]\s*\d+\s*।।", "।।", sanskrit)
    return " ".join(sanskrit.split())


def parse_gita() -> list[Verse]:
    license_url = "https://raw.githubusercontent.com/cltk/sanskrit_text_gitasupersite/master/LICENSE.md"
    license_text = fetch(license_url, RAW / "gita_supersite_LICENSE.md")
    record(
        "Bhagavad Gita Sanskrit",
        "https://github.com/cltk/sanskrit_text_gitasupersite",
        "Public Domain Mark 1.0",
        license_text.splitlines()[0] + " — CLTK mirror of Gita Supersite Sanskrit files.",
    )
    verse_url = "https://raw.githubusercontent.com/gita/gita/main/data/verse.json"
    trans_url = "https://raw.githubusercontent.com/gita/gita/main/data/translation.json"
    unlicense = fetch("https://raw.githubusercontent.com/gita/gita/main/LICENSE", RAW / "gita_gita_LICENSE")
    verses_js = json.loads(fetch(verse_url, RAW / "gita_verse.json"))
    translations = json.loads(fetch(trans_url, RAW / "gita_translation.json"))
    record(
        "Bhagavad Gita IAST + English (Purohit as packaged)",
        "https://github.com/gita/gita",
        "Unlicense (repository packaging)",
        unlicense.split("Statement of Purpose", 1)[0][:280]
        + " English field uses Shri Purohit Swami as distributed in gita/gita. "
        "The 1935 translation may still be restricted in some jurisdictions; Sanskrit is public domain.",
    )
    iast_by = {(int(v["chapter_number"]), int(v["verse_number"])): v.get("transliteration") for v in verses_js}
    english_by: dict[tuple[int, int], str] = {}
    id_to_ch_vs = {int(v["id"]): (int(v["chapter_number"]), int(v["verse_number"])) for v in verses_js}
    for row in translations:
        if row.get("authorName") != "Shri Purohit Swami":
            continue
        key = id_to_ch_vs.get(int(row["verse_id"]))
        if key:
            english_by[key] = " ".join(row.get("description", "").split())
    out: list[Verse] = []
    for chapter in range(1, 19):
        url = (
            "https://raw.githubusercontent.com/cltk/sanskrit_text_gitasupersite/master/"
            f"bhagavadgita/chapter_{chapter}_sanskrit.txt"
        )
        text = fetch(url, RAW / "gita" / f"chapter_{chapter}_sanskrit.txt")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if chapter == 13 and len(lines) == 35:
            # 701-line vulgate numbers Arjuna's extra question as 13.1.
            # Traditional 700-verse recension numbers Krishna's discourse as 13.1–34.
            # Sanskrit is copied from the source; nothing is invented or repaired.
            lines = lines[1:]
        for index, line in enumerate(lines, start=1):
            source_verse = index + 1 if chapter == 13 else index
            iast = iast_by.get((chapter, source_verse)) or iast_by.get((chapter, index))
            english = english_by.get((chapter, source_verse)) or english_by.get((chapter, index)) or ""
            if not english:
                raise RuntimeError(f"Missing licensed English for Gita {chapter}.{index}")
            out.append(Verse(
                text_id="Gita",
                chapter=str(chapter),
                verse=str(index),
                sanskrit_devanagari=strip_verse_numbers(line),
                transliteration_iast=" ".join(iast.split()) if iast else None,
                english_translation=english,
                source="CLTK Gita Supersite Sanskrit + gita/gita Purohit English",
                license="Sanskrit: Public Domain Mark 1.0 (CLTK/Gita Supersite). English: Unlicense packaging of Purohit.",
            ))
    return out


def parse_yoga() -> list[Verse]:
    license_text = (RAW / "gita_supersite_LICENSE.md").read_text(encoding="utf-8") if (
        RAW / "gita_supersite_LICENSE.md"
    ).exists() else fetch(
        "https://raw.githubusercontent.com/cltk/sanskrit_text_gitasupersite/master/LICENSE.md",
        RAW / "gita_supersite_LICENSE.md",
    )
    record(
        "Yoga Sutras Sanskrit",
        "https://github.com/cltk/sanskrit_text_gitasupersite/tree/master/yogasutra",
        "Public Domain Mark 1.0",
        license_text.splitlines()[0] + " — yogasutra/*/sutra.txt",
    )
    johnston_url = "https://www.gutenberg.org/cache/epub/2526/pg2526.txt"
    johnston = fetch(johnston_url, RAW / "johnston_yoga_sutras.txt").replace("\r\n", "\n")
    record(
        "Yoga Sutras English (Charles Johnston, 1912)",
        johnston_url,
        "Public domain (US): Project Gutenberg ebook 2526, published 1912",
        "The Yoga Sutras of Patanjali: The Book of the Spiritual Man, Charles Johnston. Gutenberg license applies to the ebook packaging.",
    )
    english = _johnston_by_pada(johnston)
    out: list[Verse] = []
    for chapter in range(1, 5):
        url = (
            "https://raw.githubusercontent.com/cltk/sanskrit_text_gitasupersite/master/"
            f"yogasutra/chapter_{chapter}/sutra.txt"
        )
        text = fetch(url, RAW / "yoga" / f"pada_{chapter}.txt")
        pairs = re.findall(r"(.+?)।।\s*(\d+)\.(\d+)\s*।।", text, flags=re.S)
        if not pairs:
            raise RuntimeError(f"Could not parse Yoga Sutras pada {chapter}")
        for sanskrit, pada, number in pairs:
            if int(pada) != chapter:
                continue
            eng = english.get((chapter, int(number)), "")
            out.append(Verse(
                text_id="YogaSutras",
                chapter=str(chapter),
                verse=str(int(number)),
                sanskrit_devanagari=" ".join(sanskrit.split()),
                transliteration_iast=None,
                english_translation=eng or f"[Johnston translation not aligned for YogaSutras {chapter}.{int(number)}]",
                source="CLTK Gita Supersite sutra.txt + Project Gutenberg 2526 (Johnston 1912)",
                license="Sanskrit: Public Domain Mark 1.0. English: public domain (Johnston 1912 / Gutenberg 2526).",
            ))
    return out


def _johnston_by_pada(text: str) -> dict[tuple[int, int], str]:
    markers = [
        (1, text.find("\n1. OM:"), text.find("\nBOOK II")),
        (2, text.find("\nBOOK II"), text.find("\nBOOK III")),
        (3, text.find("\nBOOK III"), text.find("\nBOOK IV")),
        (4, text.find("\nBOOK IV"), text.find("*** END OF THE PROJECT GUTENBERG")),
    ]
    mapped: dict[tuple[int, int], str] = {}
    numbered = re.compile(r"\n(\d+)\.\s+(.*?)(?=\n\d+\.\s|\Z)", re.S)
    for pada, start, end in markers:
        if start < 0 or end < 0 or end <= start:
            continue
        chunk = text[start:end]
        for match in numbered.finditer(chunk):
            number = int(match.group(1))
            body = " ".join(match.group(2).split())
            # Johnston prints a short translation then commentary; keep the first sentence group.
            first = re.split(r"(?<=[.!?])\s+", body, maxsplit=1)[0]
            mapped[(pada, number)] = first.strip()
    return mapped


def validate(verses: list[Verse], text_id: str, expected: dict[str, int]) -> tuple[bool, str]:
    subset = [v for v in verses if v.text_id == text_id]
    counts = Counter(v.chapter for v in subset)
    ok = dict(counts) == expected and len(subset) == sum(expected.values())
    rows = " ".join(f"ch{ch}:{counts.get(ch, 0)}/{n}" for ch, n in expected.items())
    return ok, f"{text_id:12} n={len(subset):4} expected={sum(expected.values()):4} {rows} {'OK' if ok else 'FAIL'}"


def write_sources_md() -> None:
    lines = [
        "# Corpus sources",
        "",
        f"Retrieval date: {RETRIEVED}",
        "",
        "Sanskrit is copied from the cited sources without generation, repair, or paraphrase.",
        "",
    ]
    for item in PROVENANCE:
        lines += [
            f"## {item['name']}",
            f"- URL: {item['url']}",
            f"- License: {item['license']}",
            f"- Retrieved: {item['retrieved']}",
            f"- Notes: {item['note']}",
            "",
        ]
    SOURCES_MD.write_text("\n".join(lines), encoding="utf-8")


def print_table(rows: list[str]) -> None:
    print("\n=== Corpus validation ===")
    for row in rows:
        print(row)
    print("========================\n")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    verses: list[Verse] = []
    rows: list[str] = []
    failed = False

    try:
        gita = parse_gita()
        verses.extend(gita)
        ok, row = validate(gita, "Gita", GITA_700)
        rows.append(row)
        failed = failed or not ok
    except Exception as error:
        rows.append(f"Gita         DOWNLOAD/PARSE FAIL: {error}")
        failed = True

    try:
        yoga = parse_yoga()
        verses.extend(yoga)
        ok, row = validate(yoga, "YogaSutras", YOGA_195)
        rows.append(row)
        failed = failed or not ok
    except Exception as error:
        rows.append(f"YogaSutras   DOWNLOAD/PARSE FAIL: {error}")
        failed = True

    fixture_only = [v for v in verses if "FIXTURE_ONLY" in v.license or "FIXTURE_ONLY" in v.source]
    if fixture_only:
        raise SystemExit("Refusing to write FIXTURE_ONLY records into the production corpus.")

    # A partial corpus may be useful for parser development but must never
    # silently replace a complete research corpus. Keep the last validated
    # corpus intact until every requested text passes its count check.
    if failed:
        write_sources_md()
        print_table(rows)
        print("VALIDATION FAILED — existing corpus.jsonl was left unchanged.", file=sys.stderr)
        return 1

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "corpus.jsonl").write_text(
        "\n".join(v.model_dump_json() for v in verses) + ("\n" if verses else ""),
        encoding="utf-8",
    )
    write_sources_md()
    print_table(rows)
    print(f"Wrote {len(verses)} verses to {PROCESSED / 'corpus.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
