# IKS-Verify handoff (2026-10-20)

## What changed

- The production corpus is now only Bhagavad Gita (700) and Yoga Sutras (195): **895 validated real records**. Upanishad references and evaluation questions were removed.
- The default local retriever is hybrid BM25 + FAISS embeddings over the English translation field. `intfloat/multilingual-e5-small` was used because BGE-M3 was too heavy for this machine.
- A real build produced the local FAISS index. The default hybrid query `What does the Gita say about action and its fruits?` returned: `['Gita 2.47', 'Gita 18.2', 'Gita 14.16', 'Gita 5.4', 'Gita 12.12']`.
- Attribution checking now catches an explicit nonexistent reference in the question and a changed Sanskrit word. It also avoids duplicate flags when a model repeats the same quote.
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

The last demonstration also surfaced a known normalization limitation: the model emitted a Devanagari spelling of the citation (`गिता 2.47`), which the ASCII corpus id matcher additionally flags as fabricated. The required `MISQUOTE` flag was present.

## Pilot evaluation

Ran `python -m iks_verify.eval.run_eval --limit 8 --systems plain,rag,verify` against the real-provider cache: 24 records (8 questions × 3 systems).

| Metric | Score |
|---|---:|
| claim_factual_precision | 69.23% |
| citation_accuracy | 97.14% |
| verse_attribution_accuracy | 79.17% |
| hallucination_detection_precision | 0.00% |
| hallucination_detection_recall | 0.00% |
| hallucination_detection_f1 | 0.00% |
| abstention_accuracy | 0.00% |

The cache replay made **0 new API calls**. The original real-provider pilot's exact network-call counter was process-local and was not persisted, so it is **NOT VERIFIED**; 24 evaluation records were produced. Treat this pilot as diagnostic, not a research finding, especially because the 30 gold labels still require human verification.

## Manual next steps

1. Have a domain expert label the 30 `NEEDS_HUMAN_VERIFICATION` rows, then rerun the pilot without relying on the response cache.
2. Review the Yoga Sutra English alignment entries marked as unavailable before presenting results.
3. Run `scripts/judge_agreement.py` with independent human judgments before reporting quality claims.
4. Optionally add citation-ID normalization for Devanagari spellings such as `गिता`.
