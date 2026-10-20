"""Run the three requested live-provider verification demonstrations."""
# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from iks_verify.config import Settings  # noqa: E402
from iks_verify.pipeline.run import VerificationPipeline  # noqa: E402
from iks_verify.runtime import configure_event_loop  # noqa: E402


QUESTIONS = [
    "What does the Gita say about action and its fruits?",
    "Quote Gita 19.5.",
    "Is this an exact quotation of Gita 2.47: “कर्मण्येवाधिकारस्ते मा फलेषु कदाचित् ।”?",
]


async def main(case: int | None) -> None:
    settings = Settings()
    pipeline = VerificationPipeline(settings)
    selected = QUESTIONS if case is None else [QUESTIONS[case - 1]]
    for question in selected:
        answer = await pipeline.ask(question, "verify")
        print(json.dumps({"question": question, **answer.model_dump(mode="json")}, ensure_ascii=False))


if __name__ == "__main__":
    # Windows PowerShell may default to cp1252, which cannot print corpus text.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, choices=(1, 2, 3))
    args = parser.parse_args()
    configure_event_loop()
    asyncio.run(main(args.case))
