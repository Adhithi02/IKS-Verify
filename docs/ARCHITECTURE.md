# Architecture

```mermaid
flowchart LR
  Q[Question] --> R[Hybrid retriever BM25 plus optional FAISS]
  R --> G[Grounded generator]
  G --> C[Atomic claim extraction]
  C --> V[Batched evidence verifier]
  G --> A[Deterministic attribution checks]
  V --> O[Verified answer]
  A --> O
  O --> API[FastAPI plus SSE]
  API --> UI[React parchment UI]
```

```mermaid
sequenceDiagram
  participant UI
  participant API
  participant Pipeline
  participant LLM
  UI->>API: POST /api/ask/stream
  API->>Pipeline: events(question)
  Pipeline-->>UI: retrieving / generating / extracting_claims / verifying / checking_attributions
  Pipeline->>LLM: cached, rate-limited complete()
  LLM-->>Pipeline: claims JSON then verdicts
  Pipeline-->>UI: done + VerifiedAnswer
```

Provider calls go through `iks_verify.llm`: disk cache, asyncio rate limiter (injectable clock/sleep), 429 backoff, optional fallback provider. Claim verification batches all claims in one judge call. Self-check samples default to `SELFCHECK_SAMPLES=3`. Attribution flags (fabricated citations, Sanskrit mismatch) do not use an LLM.
