# Proposed Framework

IKS-Verify combines hybrid retrieval (BM25 with an optional local FAISS / sentence-transformer index) with constrained generation, **atomic** claim extraction, batched evidence verification, and deterministic citation/quote checks. Sanskrit is ingested only from recorded public-domain or openly licensed sources; the pipeline never generates or repairs Sanskrit.

# Preliminary Evaluation

**These drafts are placeholders. Mock-mode numbers are not research findings.**

Compare four systems on 60 hand-built items (15 each: factual, fake_attribution, school_confusion, out_of_corpus):

- plain LLM
- retrieval-only (RAG)
- SelfCheck-style sampling (`SELFCHECK_SAMPLES`, default 3)
- full verify (claims + judge + attribution)

Report, after a real-provider run and human gold review: claim factual precision, citation accuracy, attribution accuracy, hallucination detection P/R/F1, abstention accuracy, provider/model ids from `python -m iks_verify.llm.check`, and judge–human agreement (percent agreement and Cohen's kappa) from `scripts/judge_agreement.py`.

Insert tables from `results/summary.md` only after (a) the corpus is validated, (b) gold verses marked `NEEDS_HUMAN_VERIFICATION` are resolved or excluded, and (c) the run is not mock-only.

# Limitations

- Free-tier LLM judges are weak on Sanskrit, recension differences, and school-specific readings.
- Corpus size is small (Gita, Yoga Sutras, and whichever Upanishads actually ingested); absence of evidence is not a claim about all Indian traditions.
- The 60-item set is hand-built; many gold verse ids remain `NEEDS_HUMAN_VERIFICATION`.
- Gita 700-verse numbering for chapter 13 follows a standard recension mapping of a 701-line source (documented in `data/SOURCES.md`).
- Model catalogues and free-tier quotas change; `--resume` is required for multi-day runs.
- English translations may be older public-domain renderings (or Unlicense-packaged Purohit); they are not a scholarly critical edition.
