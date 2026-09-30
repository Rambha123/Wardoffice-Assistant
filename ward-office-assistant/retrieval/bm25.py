"""
Keyword-based retrieval using BM25 (rank_bm25). Complements vector search:
citizens often use exact terms (form names, fee amounts, department names)
that a keyword search nails and a pure embedding search can sometimes miss.
"""

from rank_bm25 import BM25Okapi


class BM25Index:
    def __init__(self, corpus_texts: list[str], metadata: list[dict]):
        """
        corpus_texts: chunk texts, in the same order as `metadata`.
        metadata: per-chunk metadata (source, page, service) for lookups.
        """
        self.metadata = metadata
        self._tokenized_corpus = [text.lower().split() for text in corpus_texts]
        self._corpus_texts = corpus_texts
        self.bm25 = BM25Okapi(self._tokenized_corpus)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, dict, float]]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(zip(self._corpus_texts, self.metadata, scores), key=lambda x: x[2], reverse=True)
        return ranked[:top_k]


# TODO: persist/reload the BM25 index (pickle it, or rebuild from ChromaDB's
# stored documents on startup) so it doesn't need to be rebuilt every request.
