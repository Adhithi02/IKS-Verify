import csv
from pathlib import Path


def write_summary(metrics: dict[str, float], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=metrics.keys())
        writer.writeheader()
        writer.writerow(metrics)
    markdown = (
        "# MOCK EVALUATION — not research findings\n\n"
        "| Metric | Score |\n|---|---:|\n"
        + "\n".join(f"| {key} | {value:.2%} |" for key, value in metrics.items())
    )
    (output / "summary.md").write_text(markdown, encoding="utf-8")
    _write_chart(metrics, output / "metrics.svg")


def _write_chart(metrics: dict[str, float], output: Path) -> None:
    rows = []
    for index, (name, value) in enumerate(metrics.items()):
        y = 30 + index * 32
        width = round(max(0, min(1, value)) * 340)
        rows.append(
            f'<text x="10" y="{y + 14}" font-size="12">{name}</text>'
            f'<rect x="260" y="{y}" width="340" height="18" fill="#eee4d6"/>'
            f'<rect x="260" y="{y}" width="{width}" height="18" fill="#a95313"/>'
            f'<text x="610" y="{y + 14}" font-size="12">{value:.0%}</text>'
        )
    height = 70 + len(metrics) * 32
    output.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="680" '
        f'height="{height}" viewBox="0 0 680 {height}">'
        '<text x="10" y="18" font-size="12">MOCK EVALUATION — not research findings</text>'
        + "".join(rows)
        + "</svg>",
        encoding="utf-8",
    )


def export_manual_sample(records: list[dict], output: Path, size: int = 30) -> None:
    by_category: dict[str, list[dict]] = {}
    for row in records:
        by_category.setdefault(row.get("category", "unknown"), []).append(row)
    picked: list[dict] = []
    categories = list(by_category.keys()) or ["unknown"]
    index = 0
    while len(picked) < min(size, len(records)) and records:
        category = categories[index % len(categories)]
        bucket = by_category.get(category) or []
        if bucket:
            picked.append(bucket.pop(0))
        index += 1
        if index > size * 8:
            break
    if not picked:
        return
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id", "category", "system", "claim_text", "model_verdict",
                "human_verdict", "human_notes",
            ],
        )
        writer.writeheader()
        for row in picked:
            claims = row["answer"].get("claims") or [{}]
            claim = claims[0] if claims else {}
            writer.writerow({
                "id": row["id"],
                "category": row.get("category", ""),
                "system": row["system"],
                "claim_text": claim.get("text", row["answer"].get("answer", "")),
                "model_verdict": claim.get("verdict", ""),
                "human_verdict": "",
                "human_notes": "",
            })
