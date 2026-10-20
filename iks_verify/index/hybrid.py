import json
import math
import pickle
import re
from pathlib import Path

from iks_verify.schemas import Passage, Verse


def _tokens(text: str) -> list[str]:
    return re.findall(r"[\wāīūṛṝḷṃḥñṭḍṇśṣ]+", text.lower())


class SimpleBM25:
    def __init__(self, documents: list[list[str]]) -> None:
        self.documents = documents
        self.lengths = [len(doc) for doc in documents]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 1
        self.df: dict[str, int] = {}
        for doc in documents:
            for term in set(doc):
                self.df[term] = self.df.get(term, 0) + 1

    def get_scores(self, query: list[str]) -> list[float]:
        scores: list[float] = []
        total = len(self.documents)
        for doc, length in zip(self.documents, self.lengths, strict=False):
            score = 0.0
            for term in query:
                frequency = doc.count(term)
                if not frequency:
                    continue
                inverse_frequency = math.log(
                    1 + (total - self.df.get(term, 0) + 0.5) / (self.df.get(term, 0) + 0.5)
                )
                score += inverse_frequency * (frequency * 2.2) / (
                    frequency + 1.2 * (1 - 0.75 + 0.75 * length / self.average_length)
                )
            scores.append(score)
        return scores


class HybridRetriever:
    """BM25 plus optional FAISS / sentence-transformers semantic scores."""

    def __init__(
        self,
        verses: list[Verse],
        embedding_model: str | None = None,
        index_dir: Path | None = None,
        load_saved: bool = True,
    ) -> None:
        self.verses = verses
        self.documents = [
            " ".join(filter(None, [v.sanskrit_devanagari, v.transliteration_iast, v.english_translation]))
            for v in verses
        ]
        tokenized = [_tokens(document) for document in self.documents]
        try:
            from rank_bm25 import BM25Okapi

            self.bm25 = BM25Okapi(tokenized)
        except ImportError:
            self.bm25 = SimpleBM25(tokenized)
        self.embedder = None
        self.vectors = None
        self.faiss_index = None
        if load_saved and index_dir and (index_dir / "index.faiss").exists():
            self._load_saved(index_dir)
        elif embedding_model:
            self._fit_embeddings(embedding_model)

    def _fit_embeddings(self, embedding_model: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(embedding_model)
            import numpy as np

            self.vectors = self.embedder.encode(self.documents, normalize_embeddings=True)
            try:
                import faiss

                dim = int(self.vectors.shape[1])
                self.faiss_index = faiss.IndexFlatIP(dim)
                self.faiss_index.add(np.asarray(self.vectors, dtype="float32"))
            except Exception:
                self.faiss_index = None
        except Exception:
            self.embedder = None

    def save(self, index_dir: Path) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        with (index_dir / "bm25.pkl").open("wb") as handle:
            pickle.dump(self.bm25, handle)
        if self.faiss_index is not None:
            import faiss

            faiss.write_index(self.faiss_index, str(index_dir / "index.faiss"))
        if self.vectors is not None:
            import numpy as np

            np.save(index_dir / "vectors.npy", self.vectors)
        meta = {"verses": len(self.verses), "has_faiss": self.faiss_index is not None}
        (index_dir / "index_meta.json").write_text(json.dumps(meta), encoding="utf-8")

    def _load_saved(self, index_dir: Path) -> None:
        try:
            import faiss

            self.faiss_index = faiss.read_index(str(index_dir / "index.faiss"))
        except Exception:
            self.faiss_index = None
        try:
            import numpy as np

            npy = index_dir / "vectors.npy"
            if npy.exists():
                self.vectors = np.load(npy)
        except Exception:
            self.vectors = None

    @classmethod
    def from_jsonl(
        cls,
        path: Path,
        embedding_model: str | None = None,
        index_dir: Path | None = None,
    ) -> "HybridRetriever":
        verses = [
            Verse.model_validate(json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        return cls(verses, embedding_model, index_dir=index_dir)

    def retrieve(self, query: str, k: int = 5) -> list[Passage]:
        bm_scores = list(map(float, self.bm25.get_scores(_tokens(query))))
        scores = bm_scores
        if self.embedder is not None:
            import numpy as np

            query_vector = self.embedder.encode([query], normalize_embeddings=True)
            if self.faiss_index is not None:
                semantic = self.faiss_index.search(np.asarray(query_vector, dtype="float32"), len(self.verses))[0][0]
            else:
                semantic = (self.vectors @ query_vector[0]) if self.vectors is not None else bm_scores
            scores = [score + float(value) for score, value in zip(scores, semantic, strict=False)]
        elif self.faiss_index is not None and self.vectors is not None:
            # Saved FAISS without a live embedder cannot encode a new query; BM25 only.
            pass
        ranked = sorted(range(len(self.verses)), key=lambda i: scores[i], reverse=True)[:k]
        return [Passage(**self.verses[i].model_dump(), score=round(scores[i], 4)) for i in ranked]
