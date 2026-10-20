import argparse
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

from iks_verify.baselines.selfcheck import run as run_selfcheck
from iks_verify.config import Settings
from iks_verify.eval.metrics import calculate, stratified_metrics
from iks_verify.eval.report import export_manual_sample, write_stratified_summary, write_summary
from iks_verify.pipeline.run import VerificationPipeline
from iks_verify.runtime import configure_event_loop
from iks_verify.schemas import EvalRecord

SYSTEMS = ("plain", "rag", "verify", "selfcheck")


async def run(args: argparse.Namespace) -> None:
    settings = Settings(llm_provider="mock") if args.mock else Settings()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    metadata_path = output / "pilot_metadata.json"
    prior_metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if args.resume and metadata_path.exists()
        else {}
    )
    if args.fresh_cache:
        cache_dir = output / f"fresh_llm_cache_{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid.uuid4().hex[:8]}"
        settings = settings.model_copy(update={"llm_cache_dir": cache_dir})
    elif prior_metadata.get("cache_dir"):
        cache_dir = Path(prior_metadata["cache_dir"])
        settings = settings.model_copy(update={"llm_cache_dir": cache_dir})
    else:
        cache_dir = settings.llm_cache_dir
    pipeline = VerificationPipeline(settings)
    dataset = Path("iks_verify/eval/dataset/questions.jsonl")
    all_questions = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines()]
    questions = _select_questions(all_questions, args)
    systems = tuple(args.systems.split(",")) if args.systems else SYSTEMS
    for system in systems:
        if system not in SYSTEMS:
            raise SystemExit(f"unknown system {system}; choose from {','.join(SYSTEMS)}")
    records_path = output / "records.jsonl"
    completed: set[tuple[str, str]] = set()
    existing: list[dict] = []
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            existing.append(row)
            completed.add((row["id"], row["system"]))
    raw_records = list(existing)
    calls_by_system: dict[str, int] = {
        system: int(prior_metadata.get("api_calls_by_system", {}).get(system, 0))
        for system in systems
    }
    mode = "a" if args.resume and records_path.exists() else "w"
    with records_path.open(mode, encoding="utf-8") as file:
        for question in questions:
            for system in systems:
                if (question["id"], system) in completed:
                    continue
                try:
                    calls_before = pipeline.llm.calls
                    if system == "selfcheck":
                        answer = await run_selfcheck(question["question"], pipeline, settings.selfcheck_samples)
                    else:
                        answer = await pipeline.ask(question["question"], system)
                    calls_by_system[system] += pipeline.llm.calls - calls_before
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
                _write_pilot_metadata(
                    output, pipeline.llm.calls, calls_by_system, cache_dir, len(raw_records), complete=False
                )
            print(f"completed {question['id']} | {pipeline.llm.budget_line()}")
    all_records = [EvalRecord.model_validate(item) for item in raw_records]
    write_summary(calculate(all_records), output, mock=args.mock or settings.is_mock)
    _write_pilot_metadata(
        output, pipeline.llm.calls, calls_by_system, cache_dir, len(raw_records), complete=True
    )
    write_stratified_summary(stratified_metrics(all_records), output)
    export_manual_sample(raw_records, output / "manual_judge_sample.csv")
    print("MOCK EVALUATION — not research findings" if args.mock or settings.is_mock else "evaluation complete")


def _select_questions(questions: list[dict], args: argparse.Namespace) -> list[dict]:
    if not args.stratified_per_category:
        return questions[: args.limit]
    selected: list[dict] = []
    for category in ("factual", "fake_attribution", "school_confusion", "out_of_corpus"):
        bucket = [question for question in questions if question["category"] == category]
        if len(bucket) < args.stratified_per_category:
            raise SystemExit(f"not enough {category} questions for stratified sample")
        selected.extend(bucket[: args.stratified_per_category])
    return selected


def _write_pilot_metadata(
    output: Path,
    api_calls: int,
    calls_by_system: dict[str, int],
    cache_dir: Path,
    records: int,
    complete: bool,
) -> None:
    payload = {
        "api_calls": api_calls,
        "api_calls_by_system": calls_by_system,
        "cache_dir": str(cache_dir),
        "records": records,
        "complete": complete,
    }
    (output / "pilot_metadata.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--systems", type=str, default="", help="comma subset: plain,rag,verify,selfcheck")
    parser.add_argument("--output", type=str, default="results")
    parser.add_argument("--fresh-cache", action="store_true", help="use a new cache directory for live calls")
    parser.add_argument("--stratified-per-category", type=int, default=0)
    configure_event_loop()
    asyncio.run(run(parser.parse_args()))
