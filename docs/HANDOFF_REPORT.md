# 1. FILE TREE

Windows `tree` does not implement the Unix `-L` option. This is the literal output of the requested command:

```text
PS C:\Users\Adhithi C Iyer\Desktop\IKS> tree -L 3
Too many parameters - 3
```

Equivalent depth-three tree, excluding `node_modules`, `.venv`, and `data/raw`:

```text
IKS
├── .env.example
├── .gitignore
├── Makefile
├── README.md
├── data
│   ├── SOURCES.md
│   └── processed
│       └── corpus.jsonl
├── docs
│   ├── ARCHITECTURE.md
│   ├── HANDOFF_REPORT.md
│   └── PAPER_NOTES.md
├── iks_verify
│   ├── api/{main.py,routes.py,streaming.py}
│   ├── baselines/
│   ├── eval/{dataset/questions.jsonl,metrics.py,report.py,run_eval.py}
│   ├── index/hybrid.py
│   ├── ingest/{build_corpus.py,normalize.py}
│   ├── llm/{base.py,check.py,mock.py,ratelimit.py,*_client.py}
│   ├── pipeline/{attribution.py,claims.py,generate.py,run.py,verify.py}
│   ├── config.py
│   ├── runtime.py
│   ├── schemas.py
│   └── serve.py
├── results/{manual_judge_sample.csv,metrics.svg,records.jsonl,summary.csv,summary.md}
├── scripts/{build_index.py,check_eval_dataset.py,dev.ps1,download_sources.py,judge_agreement.py,make_eval_dataset.py}
├── tests/{conftest.py,fixtures/corpus.jsonl,test_api.py,test_claims.py,test_core.py}
└── web
    ├── dist/{assets,index.html}
    ├── src/{api,components,hooks,styles,App.tsx,main.tsx}
    ├── package.json
    └── vite.config.ts
```

# 2. COMMAND RESULTS

## pytest — PASS

```text
...............                                                          [100%]
15 passed in 0.82s
```

## ruff check — PASS

```text
All checks passed!
```

## npm run lint / npm test / npm run build — PASS

```text
> iks-verify-web@0.1.0 lint
> eslint .

Test Files  2 passed (2)
Tests  3 passed (3)

> iks-verify-web@0.1.0 build
> tsc -b && vite build

✓ 1597 modules transformed.
dist/index.html                            0.36 kB │ gzip:  0.26 kB
dist/assets/index-qHB0VNVj.css             8.28 kB │ gzip:  2.60 kB
dist/assets/index-DdygeNsm.js            160.20 kB │ gzip: 51.88 kB
dist/assets/html2canvas.esm-CBrSDip1.js  201.42 kB │ gzip: 48.03 kB
✓ built in 3.20s
```

## python -m iks_verify.eval.run_eval --mock --limit 10 — PASS

```text
completed f01 | API calls: 6 | est. remaining daily budget: 994
completed f02 | API calls: 12 | est. remaining daily budget: 988
completed f03 | API calls: 18 | est. remaining daily budget: 982
completed f04 | API calls: 24 | est. remaining daily budget: 976
completed f05 | API calls: 30 | est. remaining daily budget: 970
completed f06 | API calls: 36 | est. remaining daily budget: 964
completed f07 | API calls: 42 | est. remaining daily budget: 958
completed f08 | API calls: 48 | est. remaining daily budget: 952
completed f09 | API calls: 54 | est. remaining daily budget: 946
completed f10 | API calls: 60 | est. remaining daily budget: 940
MOCK EVALUATION — not research findings
```

## python -m iks_verify.serve and /api/health — PASS

The local server was started, queried, and stopped. The real local response was:

```json
{"status":"ok","provider":"groq","model":"openai/gpt-oss-120b","mock_mode":false,"api_calls":0}
```

# 3. CORPUS STATUS

The production corpus contains **895 REAL data** records: 700 Bhagavad Gita verses and 195 Yoga Sutras. The Upanishads below are **NOT INGESTED**, not fixtures. The corpus-wide validator intentionally fails until they are added; it did not overwrite the existing corpus.

| Text | Verses | Source URL(s) | Licence | Status |
| --- | ---: | --- | --- | --- |
| Bhagavad Gita | 700 | `github.com/cltk/sanskrit_text_gitasupersite`; `github.com/gita/gita` | Sanskrit: Public Domain Mark 1.0. English packaging: Unlicense; see translation caveat in `data/SOURCES.md`. | REAL data |
| Yoga Sutras | 195 | `github.com/cltk/sanskrit_text_gitasupersite`; `gutenberg.org/cache/epub/2526/pg2526.txt` | Sanskrit: Public Domain Mark 1.0. English: public-domain US (Johnston 1912). | REAL data |
| Isha Upanishad | 0 / 18 | No vetted verse-aligned source selected | Not verified | NOT INGESTED |
| Kena Upanishad | 0 / 34 | No vetted verse-aligned source selected | Not verified | NOT INGESTED |
| Katha Upanishad | 0 / 119 | No vetted verse-aligned source selected | Not verified | NOT INGESTED |
| Mandukya Upanishad | 0 / 12 | No vetted verse-aligned source selected | Not verified | NOT INGESTED |

Five spot-check verses sampled from the ingested corpus:

```text
Gita | 1 | 1  | धृतराष्ट्र उवाच धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः। मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय।।
Gita | 4 | 18 | कर्मण्यकर्म यः पश्येदकर्मणि च कर्म यः। स बुद्धिमान् मनुष्येषु स युक्तः कृत्स्नकर्मकृत्।।
Gita | 9 | 21 | ते तं भुक्त्वा स्वर्गलोकं विशालं क्षीणे पुण्ये मर्त्यलोकं विशन्ति। एव त्रयीधर्ममनुप्रपन्ना गतागतं कामकामा लभन्ते।।
Gita | 14 | 15 | रजसि प्रलयं गत्वा कर्मसङ्गिषु जायते। तथा प्रलीनस्तमसि मूढयोनिषु जायते।।
YogaSutras | 1 | 17 | वितर्कविचारानन्दास्मितारूपानुगमात्संप्रज्ञातः
```

# 4. PROVIDER STATUS

Implemented providers: `mock`, `groq`, `gemini`, `openrouter`, `openai`, and `anthropic`.

- **Groq: real API verified.** `/models` returned 11 models; `openai/gpt-oss-120b` was present for both configured fields; a real `pong` request succeeded. One real end-to-end `/api/ask` request also succeeded.
- **Mock: verified** through unit tests and the 10-question mock evaluation.
- **Gemini, OpenRouter, OpenAI, Anthropic: mock/code-path only; NOT VERIFIED against a real API.**
- `.env.example` defaults: `LLM_PROVIDER=mock`, `LLM_MODEL=openai/gpt-oss-20b`, `JUDGE_MODEL=openai/gpt-oss-20b`.

# 5. PIPELINE WALKTHROUGH

Fresh mock-mode run against `data/processed/corpus.jsonl`:

```json
{
  "question": "What does the Gita say about action and its fruits?",
  "retrieved_verse_ids": ["Gita 18.10", "Gita 18.2", "Gita 4.17", "Gita 2.28", "Gita 18.31"],
  "answer": "The wise man who has attained purity, whose doubts are resolved, who is filled with the spirit of self-abnegation, does not shy away from action due to its pain, nor does he crave it due to its pleasure [Gita 18.10]. Lord Shri Krishna replied: The sages say that renunciation is forgoing an action that springs from desire, and relinquishing is the surrender of its fruit [Gita 18.2].",
  "claims": [
    {"text":"The wise man who has attained purity, whose doubts are resolved, who is filled with the spirit of self-abnegation, does not shy away from action due to its pain, nor does he crave it due to its pleasure [Gita 18.10].","citations":["Gita 18.10"],"verdict":"SUPPORTED","supporting_verse_ids":["Gita 18.10"],"rationale":"Supported by retrieved evidence."},
    {"text":"Lord Shri Krishna replied: The sages say that renunciation is forgoing an action that springs from desire, and relinquishing is the surrender of its fruit [Gita 18.2].","citations":["Gita 18.2"],"verdict":"SUPPORTED","supporting_verse_ids":["Gita 18.2"],"rationale":"Supported by retrieved evidence."}
  ],
  "attribution_flags": [],
  "trust_score": 1.0
}
```

# 6. EVAL DATASET

There are 60 questions: `factual` 15, `fake_attribution` 15, `school_confusion` 15, and `out_of_corpus` 15. The schema/balance checker passed.

`gold_verses = NEEDS_HUMAN_VERIFICATION`:

```text
f04, f05, f06, f08, f09, f10, f11, f12, f13, f14, f15,
a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15,
s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15,
o01, o02, o03, o04, o05, o06, o07, o08, o09, o10, o11, o12, o13, o14, o15
```

# 7. UI CHECKLIST

| UI feature | Status | Component file(s) |
| --- | --- | --- |
| Hero, question box, and examples | DONE | `web/src/App.tsx`, `components/AskBox.tsx`, `components/ExampleChips.tsx` |
| Plain/RAG/Verify/Self-check selector | DONE | `components/SystemToggle.tsx` |
| Live pipeline progress | PARTIAL — SSE code and parser tests pass; browser walk-through NOT VERIFIED | `components/PipelineProgress.tsx`, `hooks/useAsk.ts` |
| Inline claim highlighting and hover evidence | PARTIAL — highlights/tooltips exist; inline click-to-drawer is not implemented | `components/AnswerPanel.tsx` |
| Trust meter and verdict breakdown | DONE | `components/TrustMeter.tsx` |
| Attribution alerts and quote diff | DONE | `components/AttributionAlert.tsx` |
| Evidence drawer linked to selected claim | DONE | `components/EvidenceDrawer.tsx`, `components/VerseCard.tsx` |
| Compare mode | DONE | `components/CompareView.tsx` |
| Abstention state | DONE | `components/AnswerPanel.tsx` |
| Rate-limit countdown | DONE | `hooks/useAsk.ts`, `App.tsx` |
| Loading skeleton, errors, basic ARIA | PARTIAL — focus-management behaviour is NOT VERIFIED | `App.tsx`, `components/*.tsx` |
| Provider/model footer and mock indicator | DONE | `App.tsx` |
| JSON and PNG export | DONE | `components/AnswerPanel.tsx` |

# 8. KNOWN ISSUES AND SHORTCUTS

- The research corpus is incomplete: Isha, Kena, Katha, and Mandukya are not ingested. The global corpus validator therefore reports failure by design.
- The downloaded Gita English field comes from the `gita/gita` Purohit packaging; its repository is Unlicense, but the 1935 translation has a jurisdictional caveat documented in `data/SOURCES.md`.
- Local FAISS/sentence-transformer retrieval is optional and **NOT VERIFIED**. BM25 retrieval is verified.
- The mock evaluator is deterministic and is explicitly not a research result. Mock cache entries are now namespaced away from real-provider cache entries.
- Most gold labels need subject-matter review before metrics can be published.
- Only Groq has a real-API verification. Other provider integrations are **NOT VERIFIED** with real keys.
- Browser-level manual UX/accessibility testing is **NOT VERIFIED**, although lint, unit tests, and the production build pass.
- `npm audit fix` reduced the dependency tree but development-only advisories remain; production-only audit had no reported vulnerabilities. Do not use a breaking `npm audit fix --force` without reviewing Vite/Vitest upgrades.
- Initial local Git commit created: `8dfcf0b` (`Build verified IKS-Verify research prototype`).

# 9. MY MANUAL TODO LIST

1. Obtain a legally reusable, verse-aligned Devanagari plus public-domain/open translation edition for Isha, Kena, Katha, and Mandukya. Record exact URLs and licences in `data/SOURCES.md`; do not generate Sanskrit.
2. Implement and review the four Upanishad parsers in `scripts/download_sources.py`, then run the corpus validator until all expected counts pass.
3. Have a Sanskrit/IKS subject-matter expert verify every `NEEDS_HUMAN_VERIFICATION` label and all five sampled verses against the selected editions.
4. Install `requirements-local-embeddings.txt`, build the optional local index, and compare it with the verified BM25 baseline.
5. Run a small, budgeted real-provider evaluation and later resume it with `--resume`; do not publish mock metrics as results.
6. Complete `results/manual_judge_sample.csv` with independent human labels, then run `scripts/judge_agreement.py` and report agreement.
7. Manually test the built UI in a browser, especially keyboard focus, the SSE progress flow, mobile evidence drawer, rate-limit countdown, and JSON/PNG downloads.
8. Review outstanding development dependency advisories before upgrading Vite/Vitest.
9. Before further work, review `git status` and `git log --oneline`; the initial project commit already exists (`8dfcf0b`).
