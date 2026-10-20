# ruff: noqa: E402, I001
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The path adjustment supports direct `python scripts/build_index.py` use.
from iks_verify.config import get_settings  # noqa: E402
from iks_verify.index.hybrid import HybridRetriever

settings = get_settings()
models = [settings.embedding_model, settings.embedding_fallback_model]
last_error: Exception | None = None
retriever = None
for model in dict.fromkeys(models):
    try:
        candidate = HybridRetriever.from_jsonl(settings.corpus_path, embedding_model=model, index_dir=None)
        if candidate.embedder is None or candidate.faiss_index is None:
            raise RuntimeError("embedding model or FAISS index was unavailable")
        retriever = candidate
        print(f"Embedding model selected: {model}")
        break
    except Exception as error:
        last_error = error
        print(f"Embedding model failed: {model} ({error})")
if retriever is None:
    raise SystemExit(f"Could not build a hybrid index: {last_error}")
try:
    retriever.save(settings.index_dir)
    faiss_state = "FAISS saved" if retriever.faiss_index is not None else "BM25 only (FAISS unavailable)"
except Exception as error:
    faiss_state = f"index save skipped: {error}"
print(f"Corpus ready: {len(retriever.verses)} verses ({faiss_state})")
