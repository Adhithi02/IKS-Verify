from iks_verify.schemas import EvalRecord, Verdict


def calculate(records: list[EvalRecord]) -> dict[str, float]:
    all_claims = [claim for record in records for claim in record.answer.claims]
    supported = sum(claim.verdict == Verdict.SUPPORTED for claim in all_claims)
    citations = [citation for claim in all_claims for citation in claim.citations]
    valid_citations = [citation for claim in all_claims for citation in claim.supporting_verse_ids]
    abstentions = [record for record in records if record.should_abstain]
    correct_abstentions = sum(record.answer.abstained for record in abstentions)
    flags = sum(bool(record.answer.attribution_flags) for record in records)
    return {
        "claim_factual_precision": supported / len(all_claims) if all_claims else 0.0,
        "citation_accuracy": len(valid_citations) / len(citations) if citations else 0.0,
        "verse_attribution_accuracy": 1 - flags / len(records) if records else 0.0,
        "hallucination_detection_precision": 0.0,
        "hallucination_detection_recall": 0.0,
        "hallucination_detection_f1": 0.0,
        "abstention_accuracy": correct_abstentions / len(abstentions) if abstentions else 0.0,
    }


def stratified_metrics(records: list[EvalRecord]) -> dict[str, dict]:
    """Return reproducible per-system and per-category pilot metrics."""
    systems = sorted({record.system for record in records})
    categories = sorted({record.category for record in records})
    result: dict[str, dict] = {"systems": {}}
    for system in systems:
        system_records = [record for record in records if record.system == system]
        result["systems"][system] = _metric_group(system_records)
        result["systems"][system]["categories"] = {
            category: _metric_group([record for record in system_records if record.category == category])
            for category in categories
        }
    return result


def _metric_group(records: list[EvalRecord]) -> dict[str, float | int | None]:
    claims = [claim for record in records for claim in record.answer.claims]
    supported = sum(claim.verdict == Verdict.SUPPORTED for claim in claims)
    fake_records = [record for record in records if record.category == "fake_attribution"]
    fake_catches = sum(
        any(flag.kind == "FABRICATED_CITATION" for flag in record.answer.attribution_flags)
        for record in fake_records
    )
    ooc_records = [record for record in records if record.category == "out_of_corpus"]
    ooc_abstentions = sum(record.answer.abstained for record in ooc_records)
    return {
        "records": len(records),
        "claim_precision": supported / len(claims) if claims else None,
        "fabricated_citation_catch_rate": fake_catches / len(fake_records) if fake_records else None,
        "out_of_corpus_abstention_rate": ooc_abstentions / len(ooc_records) if ooc_records else None,
    }
