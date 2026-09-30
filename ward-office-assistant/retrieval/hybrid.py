"""
Combines BM25 (keyword) and vector (semantic) retrieval into a single
ranked result list — one of the "advanced beyond basic RAG" pieces to
highlight to the supervisor, since a plain vector-only RAG demo is common
but hybrid retrieval + reranking is not.

Common combination strategy: reciprocal rank fusion (RRF), which merges
two ranked lists without needing to normalize incompatible score scales.
"""

from . import bm25 as bm25_module
from . import vector as vector_module


def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """
    ranked_lists: each is a list of chunk ids, best-first, from one retriever.
    Returns a single fused ranking of chunk ids.

    RRF score for a chunk = sum over lists of 1 / (k + rank_in_that_list)
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def hybrid_search(query: str, query_embedding: list[float], top_k: int = 10):
    """
    TODO:
        1. bm25_results = bm25_index.search(query, top_k=top_k * 2)
        2. vector_results = vector.similarity_search(query_embedding, top_k=top_k * 2)
        3. fused_ids = reciprocal_rank_fusion([
               [r[1]["id"] for r in bm25_results],
               [r["id"] for r in vector_results],
           ])
        4. return the top_k chunks (with text + metadata) in fused order.
    """
    raise NotImplementedError
