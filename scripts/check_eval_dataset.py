import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {"id", "category", "question", "gold_answer_notes", "gold_verses", "should_abstain"}
CATEGORIES = {"factual", "fake_attribution", "school_confusion", "out_of_corpus"}


def main(path: Path) -> int:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    missing = [i for i, row in enumerate(rows, 1) if not REQUIRED <= set(row)]
    if missing:
        print(f"schema FAIL: missing keys on lines {missing}")
        return 1
    counts = Counter(row["category"] for row in rows)
    print("n=", len(rows), dict(counts))
    if set(counts) - CATEGORIES:
        print("unknown categories", set(counts) - CATEGORIES)
        return 1
    if len(rows) != 60 or any(counts[cat] != 15 for cat in CATEGORIES):
        print("balance FAIL: need 15 of each category, 60 total")
        return 1
    print("dataset schema and balance OK")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("iks_verify/eval/dataset/questions.jsonl")
    raise SystemExit(main(target))
