from iks_verify.config import get_settings
from iks_verify.index.hybrid import HybridRetriever

settings = get_settings()
retriever = HybridRetriever.from_jsonl(
    settings.corpus_path,
    embedding_model=settings.embedding_model,
    index_dir=None,
)
try:
    retriever.save(settings.index_dir)
    faiss_state = "FAISS saved" if retriever.faiss_index is not None else "BM25 only (FAISS unavailable)"
except Exception as error:
    faiss_state = f"index save skipped: {error}"
print(f"Corpus ready: {len(retriever.verses)} verses ({faiss_state})")
