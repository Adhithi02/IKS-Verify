# IKS-Verify handoff (2026-10-20)

## What changed

- The production corpus is now only Bhagavad Gita (700) and Yoga Sutras (195): **895 validated real records**. Upanishad references and evaluation questions were removed.
- The default local retriever is hybrid BM25 + FAISS embeddings over Sanskrit, IAST, and English fields. `intfloat/multilingual-e5-small` was used because BGE-M3 was too heavy for this machine.
- A real build produced the local FAISS index. The default hybrid query `What does the Gita say about action and its fruits?` returned: `['Gita 2.47', 'Gita 18.2', 'Gita 14.16', 'Gita 5.4', 'Gita 12.12']`.
- Attribution checking now catches an explicit nonexistent reference in the question and a changed Sanskrit word. It also avoids duplicate flags when a model repeats the same quote.
- Citation IDs now canonicalize ASCII and Devanagari text names, and closest IDs retain corpus casing.
- API-call counts are persisted in each cache as `api_call_count.txt` and in pilot metadata.
- All factual and school-confusion evaluation links are now `NEEDS_HUMAN_VERIFICATION` (**30** labels). Fake-attribution rows use nonexistent chapter/verse references and `gold_verses: []`; out-of-corpus rows use `should_abstain: true` and `gold_verses: []`.

## Command results

```text
pytest --basetemp .pytest-tmp
15 passed, 1 warning in 23.47s

ruff check .
All checks passed!

npm test
Test Files  2 passed (2)
Tests  3 passed (3)

npm run build
✓ 1597 modules transformed.
✓ built in 6.23s

corpus validator
Gita         700 / 700  OK
YogaSutras   195 / 195  OK
Validated 895 verses
```

The pytest warning is only an inaccessible pre-existing `.pytest_cache` entry in the execution sandbox; the tests passed using the project-local base temp directory.

## Real Groq demonstrations

The three demonstrations used the configured Groq provider and `openai/gpt-oss-120b`. Responses were cached locally after the real calls; the output was reprinted from that cache to avoid repeat charges. The default hybrid retrieval was tested separately above.

```json
{"case":"normal factual","question":"What does the Gita say about action and its fruits?","retrieved_ids":["Gita 2.47","Gita 18.2","Gita 14.16","Gita 18.10","Gita 18.31"],"claim_verdicts":["SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED","SUPPORTED"],"attribution_flags":[],"trust_score":1.0,"abstained":false}
{"case":"nonexistent citation","question":"Quote Gita 19.5.","retrieved_ids":["YogaSutras 2.5","Gita 11.19","Gita 1.1","Gita 1.2","Gita 1.3"],"attribution_flags":[{"kind":"FABRICATED_CITATION","cited":"Gita 19.5","closest_verse_id":"gita 1.5"}],"trust_score":0.0,"abstained":true}
{"case":"changed Sanskrit word","question":"Is this an exact quotation of Gita 2.47: … कदाचित् …?","retrieved_ids":["Gita 2.47","Gita 3.8","Gita 14.16","Gita 18.6","Gita 18.9"],"attribution_flags":[{"kind":"MISQUOTE","closest_verse_id":"Gita 2.47","actual_text":"corpus text for Gita 2.47"}],"trust_score":0.6,"abstained":true}
```

The citation normalization fix covers Devanagari spellings such as `गिता 2.47` without fabricating a citation flag.

## Final stratified pilot

Ran `python -m iks_verify.eval.run_eval --stratified-per-category 4 --systems plain,rag,verify --output results\final_pilot --fresh-cache`, resuming only across provider rate windows with the same fresh cache. This produced 48 records (4 questions × 4 categories × 3 systems) and **116 real API calls**, persisted in `results\final_pilot\pilot_metadata.json`.

| System | Claim precision | Fabricated-citation catch rate | Out-of-corpus abstention rate |
|---|---:|---:|---:|
| plain | 15.24% | 100.00% | 0.00% |
| rag | — | 0.00% | 100.00% |
| verify | 57.41% | 100.00% | 100.00% |

Per-system/per-category metrics are in [`results/final_pilot/stratified_summary.md`](../results/final_pilot/stratified_summary.md). The persisted call counter includes provider retries/rate-window attempts; successful-record attribution by system was plain 40, rag 16, verify 36. Treat these results as diagnostic, especially because the 30 gold labels still require human verification.

## Yoga Sutras retrieval check

There are **2** Yoga Sutras verses lacking an aligned English translation. Three local retrieval checks returned:

```text
what is yoga        -> YogaSutras 2.28, Gita 3.7, YogaSutras 2.29, Gita 6.20, Gita 8.8
eight limbs of yoga -> YogaSutras 2.29, YogaSutras 2.28, Gita 2.58, Gita 11.16, Gita 3.7
posture             -> Gita 6.11, Gita 1.11, Gita 1.1, Gita 1.3, Gita 1.2
```

The source corpus has no IAST values for the Yoga Sutras, so there were no IAST fields to index for those 195 records.

## Repository hygiene

```text
git ls-files .env
NOT TRACKED
```

## Manual next steps

1. Have a domain expert label the 30 `NEEDS_HUMAN_VERIFICATION` rows, then rerun the pilot without relying on the response cache.
2. Review the two Yoga Sutra English alignment entries marked as unavailable before presenting results.
3. Run `scripts/judge_agreement.py` with independent human judgments before reporting quality claims.
