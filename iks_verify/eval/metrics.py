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
