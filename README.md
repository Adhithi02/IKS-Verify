# IKS-Verify

IKS-Verify is a research prototype for retrieval-grounded question answering, claim verification, and deterministic verse-attribution checks over Indian Knowledge System texts.

## Windows quickstart (PowerShell)

1. Python 3.11+ and Node.js LTS. From the repo root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\scripts\dev.ps1 setup
```

2. `scripts/dev.ps1` targets:

| Target | What it does |
| --- | --- |
| `.\scripts\dev.ps1 setup` | pip install + `npm install` in `web/` |
| `.\scripts\dev.ps1 serve` | production API (`python -m iks_verify.serve`, serves `web/dist` if built) |
| `.\scripts\dev.ps1 dev` | prints the two-window API + Vite commands |
| `.\scripts\dev.ps1 test` | pytest (fixture corpus) + `npm test` |
| `.\scripts\dev.ps1 lint` | ruff + `npm run lint` |

3. Dev UI: one terminal `.\scripts\dev.ps1 serve`, another `Set-Location .\web; npm run dev`. Production UI: `Set-Location .\web; npm run build` then `.\scripts\dev.ps1 serve`.

There is a Makefile for Unix; on Windows use `scripts/dev.ps1`.

## Free Groq / Gemini key and model selection

1. Groq: create a key at [console.groq.com](https://console.groq.com). Gemini: [aistudio.google.com](https://aistudio.google.com).
2. Put the key in `.env` (`GROQ_API_KEY` or `GEMINI_API_KEY`). Never commit `.env`.
3. Set `LLM_PROVIDER=groq` (or `gemini`). `.env.example` uses Groq's current
   economical default, `openai/gpt-oss-20b`; change it only after checking the
   models available to your account.
4. Run:

```powershell
.\.venv\Scripts\python.exe -m iks_verify.llm.check
```

That command lists `/models` (or Gemini equivalent), prints the configured names, warns if they are missing from the list, and makes one tiny test call. **Pick a currently listed Groq model** (often a gpt-oss or Llama family name). Do not copy stale names from old docs.

## Corpus and index (Gita + Yoga Sutras)

```powershell
.\.venv\Scripts\python.exe scripts\download_sources.py
.\.venv\Scripts\python.exe -m iks_verify.ingest.build_corpus data\processed\corpus.jsonl
.\.venv\Scripts\python.exe -m pip install -r requirements-local-embeddings.txt
.\.venv\Scripts\python.exe scripts\build_index.py
```

Licenses and retrieval dates are recorded in `data/SOURCES.md`. Sanskrit is never generated. Fixtures live only in `tests/fixtures/`.

## Evaluation (including across days)

Mock (offline):

```powershell
$env:LLM_PROVIDER='mock'
.\.venv\Scripts\python.exe -m iks_verify.eval.run_eval --mock --limit 60
```

Real key, small batch, subset of systems, then resume later if you hit quota:

```powershell
.\.venv\Scripts\python.exe -m iks_verify.eval.run_eval --limit 5 --systems verify
.\.venv\Scripts\python.exe -m iks_verify.eval.run_eval --resume --limit 60 --systems plain,rag,verify,selfcheck
```

`--resume` skips id+system pairs already in `results/records.jsonl`. Outputs are labelled **MOCK EVALUATION** when run with `--mock`. After you fill `human_verdict` in `results/manual_judge_sample.csv`, run `.\.venv\Scripts\python.exe scripts\judge_agreement.py`.
