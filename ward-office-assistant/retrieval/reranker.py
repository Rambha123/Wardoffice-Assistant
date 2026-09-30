"""
Optional cross-encoder reranking step applied to the top-N candidates from
hybrid_search() before sending the final top_k to Gemini. A cross-encoder
scores (query, chunk) pairs jointly, which is more accurate than embedding
similarity alone but too slow to run over the whole corpus — hence
"retrieve broad with hybrid search, then rerank a small candidate set".

Another "advanced" feature to highlight vs. a basic RAG chatbot.
"""


def rerank(query: str, candidates: list[str], top_k: int = 5) -> list[str]:
    """
    TODO: use a cross-encoder such as
    'cross-encoder/ms-marco-MiniLM-L-6-v2' (or a multilingual variant, given
    English/Nepali mixed queries) via sentence-transformers:

        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [(query, c) for c in candidates]
        scores = model.predict(pairs)
        ranked = [c for _, c in sorted(zip(scores, candidates), reverse=True)]
        return ranked[:top_k]

    If a multilingual cross-encoder proves hard to find, an acceptable
    fallback is skipping reranking and relying on hybrid_search() alone —
    note that trade-off explicitly in docs/architecture.md.
    """
    return candidates[:top_k]
