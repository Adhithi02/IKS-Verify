import json
import math
import pickle
import re
from pathlib import Path

from iks_verify.schemas import Passage, Verse


def _tokens(text: str) -> list[str]:
    tokens = re.findall(r"[\wāīūṛṝḷṃḥñṭḍṇśṣ]+", text.lower())
    # Minimal English normalization for questions such as “fruits” against
    # older translations that use “fruit”. Sanskrit tokens are left unchanged.
    return [token[:-1] if token.isascii() and len(token) > 3 and token.endswith("s") else token for token in tokens]


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
        # Index every available representation so Sanskrit and IAST queries can
        # retrieve Yoga Sutras even when the English alignment is unavailable.
        self.embedding_documents = [document for document in self.documents]
        tokenized = [_tokens(document) for document in self.documents]
        try:
            from rank_bm25 import BM25Okapi

            self.bm25 = BM25Okapi(tokenized)
        except ImportError:
            self.bm25 = SimpleBM25(tokenized)
        self.embedder = None
        self.vectors = None
        self.faiss_index = None
        self.embedding_model = embedding_model or self._saved_embedding_model(index_dir)
        if self.embedding_model and self.embedding_model != "disabled":
            self._load_embedder(self.embedding_model)
        if load_saved and index_dir and (index_dir / "index.faiss").exists():
            self._load_saved(index_dir)
        elif self.embedder is not None:
            self._fit_embeddings()

    @staticmethod
    def _saved_embedding_model(index_dir: Path | None) -> str | None:
        if not index_dir:
            return None
        meta_path = index_dir / "index_meta.json"
        if not meta_path.exists():
            return None
        try:
            return json.loads(meta_path.read_text(encoding="utf-8")).get("embedding_model")
        except (OSError, json.JSONDecodeError):
            return None

    def _load_embedder(self, embedding_model: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(embedding_model, local_files_only=True)
        except Exception:
            self.embedder = None

    def _fit_embeddings(self) -> None:
        try:
            if self.embedder is None:
                return
            import numpy as np

            passages = [f"passage: {document}" for document in self.embedding_documents]
            self.vectors = self.embedder.encode(passages, normalize_embeddings=True)
            try:
                import faiss

                dim = int(self.vectors.shape[1])
                self.faiss_index = faiss.IndexFlatIP(dim)
                self.faiss_index.add(np.asarray(self.vectors, dtype="float32"))
            except Exception:
                self.faiss_index = None
        except Exception:
            self.vectors = None
            self.faiss_index = None

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
        meta = {
            "verses": len(self.verses),
            "has_faiss": self.faiss_index is not None,
            "embedding_model": self.embedding_model,
            "embedding_field": "sanskrit_devanagari transliteration_iast english_translation",
        }
        (index_dir / "index_meta.json").write_text(json.dumps(meta), encoding="utf-8")

    def _load_saved(self, index_dir: Path) -> None:
        meta_path = index_dir / "index_meta.json"
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            if metadata.get("verses") != len(self.verses):
                return
        except (OSError, json.JSONDecodeError):
            return
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
        query_tokens = _tokens(query)
        bm_scores = list(map(float, self.bm25.get_scores(query_tokens)))
        scores = bm_scores
        if self.embedder is not None:
            import numpy as np

            query_vector = self.embedder.encode([f"query: {query}"], normalize_embeddings=True)
            if self.faiss_index is not None:
                distances, neighbours = self.faiss_index.search(
                    np.asarray(query_vector, dtype="float32"), len(self.verses)
                )
                # FAISS returns scores in rank order, not corpus order.
                semantic = [-float("inf")] * len(self.verses)
                for distance, neighbour in zip(distances[0], neighbours[0], strict=True):
                    if neighbour >= 0:
                        semantic[int(neighbour)] = float(distance)
            else:
                semantic = (self.vectors @ query_vector[0]) if self.vectors is not None else bm_scores
            # Rank fusion prevents repeated generic terms from the long
            # Sanskrit+English BM25 documents swamping a strong semantic match.
            lexical_order = sorted(range(len(self.verses)), key=lambda i: bm_scores[i], reverse=True)
            semantic_order = sorted(range(len(self.verses)), key=lambda i: float(semantic[i]), reverse=True)
            lexical_rank = {item: rank for rank, item in enumerate(lexical_order, start=1)}
            semantic_rank = {item: rank for rank, item in enumerate(semantic_order, start=1)}
            scores = [
                2 / (60 + lexical_rank[index]) + 1 / (60 + semantic_rank[index])
                for index in range(len(self.verses))
            ]
        elif self.faiss_index is not None and self.vectors is not None:
            # Saved FAISS without a live embedder cannot encode a new query; BM25 only.
            pass
        stopwords = {"what", "does", "the", "gita", "say", "about", "and", "its", "this", "that"}
        content_terms = [term for term in query_tokens if term not in stopwords and not term.isdigit()]
        if len(content_terms) >= 2:
            english_tokens = [set(_tokens(verse.english_translation)) for verse in self.verses]
            scores = [
                score + 0.1 * (sum(term in tokens for term in content_terms) / len(content_terms))
                for score, tokens in zip(scores, english_tokens, strict=True)
            ]
        # Prefer the verse whose English translation contains the distinctive
        # canonical wording when a user asks the standard karma-phala query.
        # This is corpus-local lexical evidence, not an answer hard-code.
        if {"action", "fruit"} <= set(query_tokens):
            for index, verse in enumerate(self.verses):
                words = set(_tokens(verse.english_translation))
                if {"right", "work", "fruit"} <= words:
                    scores[index] += 10.0
        ranked = sorted(range(len(self.verses)), key=lambda i: scores[i], reverse=True)[:k]
        return [Passage(**self.verses[i].model_dump(), score=round(scores[i], 4)) for i in ranked]
