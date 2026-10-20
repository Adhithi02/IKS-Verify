import argparse
import asyncio
import json
from pathlib import Path

from iks_verify.baselines.selfcheck import run as run_selfcheck
from iks_verify.config import Settings
from iks_verify.eval.metrics import calculate
from iks_verify.eval.report import export_manual_sample, write_summary
from iks_verify.pipeline.run import VerificationPipeline
from iks_verify.runtime import configure_event_loop
from iks_verify.schemas import EvalRecord

SYSTEMS = ("plain", "rag", "verify", "selfcheck")


async def run(args: argparse.Namespace) -> None:
    settings = Settings(llm_provider="mock") if args.mock else Settings()
    pipeline = VerificationPipeline(settings)
    dataset = Path("iks_verify/eval/dataset/questions.jsonl")
    questions = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines()][: args.limit]
    systems = tuple(args.systems.split(",")) if args.systems else SYSTEMS
    for system in systems:
        if system not in SYSTEMS:
            raise SystemExit(f"unknown system {system}; choose from {','.join(SYSTEMS)}")
    output = Path("results")
    output.mkdir(exist_ok=True)
    records_path = output / "records.jsonl"
    completed: set[tuple[str, str]] = set()
    existing: list[dict] = []
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            existing.append(row)
            completed.add((row["id"], row["system"]))
    raw_records = list(existing)
    mode = "a" if args.resume and records_path.exists() else "w"
    with records_path.open(mode, encoding="utf-8") as file:
        for question in questions:
            for system in systems:
                if (question["id"], system) in completed:
                    continue
                try:
                    if system == "selfcheck":
                        answer = await run_selfcheck(question["question"], pipeline, settings.selfcheck_samples)
                    else:
                        answer = await pipeline.ask(question["question"], system)
                except Exception as error:
                    if "429" in str(error) or "quota" in str(error).lower():
                        print("quota reached, rerun with --resume later")
                        print(pipeline.llm.budget_line())
                        return
                    raise
                record = EvalRecord(
                    id=question["id"],
                    category=question["category"],
                    system=system,
                    answer=answer,
                    gold_verses=question["gold_verses"],
                    should_abstain=question["should_abstain"],
                )
                serialized = record.model_dump(mode="json")
                raw_records.append(serialized)
                file.write(json.dumps(serialized) + "\n")
                file.flush()
            print(f"completed {question['id']} | {pipeline.llm.budget_line()}")
    all_records = [EvalRecord.model_validate(item) for item in raw_records]
    write_summary(calculate(all_records), output)
    export_manual_sample(raw_records, output / "manual_judge_sample.csv")
    print("MOCK EVALUATION — not research findings" if args.mock or settings.is_mock else "evaluation complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--systems", type=str, default="", help="comma subset: plain,rag,verify,selfcheck")
    configure_event_loop()
    asyncio.run(run(parser.parse_args()))
