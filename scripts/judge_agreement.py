"""Compute percent agreement and Cohen's kappa from a filled manual_judge_sample.csv."""
import csv
import sys
from pathlib import Path


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    agree = sum(a == b for a, b in pairs) / n
    labels = sorted({label for pair in pairs for label in pair})
    p_e = 0.0
    for label in labels:
        p1 = sum(a == label for a, _ in pairs) / n
        p2 = sum(b == label for _, b in pairs) / n
        p_e += p1 * p2
    if p_e == 1:
        return 1.0
    return (agree - p_e) / (1 - p_e)


def main(path: Path) -> int:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    pairs = [
        (row["model_verdict"].strip(), row["human_verdict"].strip())
        for row in rows
        if row.get("human_verdict", "").strip()
    ]
    if not pairs:
        print("No human_verdict values filled yet.")
        return 0
    agree = sum(a == b for a, b in pairs) / len(pairs)
    print(f"n={len(pairs)} percent_agreement={agree:.3f} cohens_kappa={kappa(pairs):.3f}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/manual_judge_sample.csv")
    raise SystemExit(main(target))
