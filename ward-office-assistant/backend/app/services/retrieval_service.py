"""
Thin wrapper around the top-level `retrieval/` package (hybrid.py, bm25.py,
vector.py, reranker.py) so the API layer doesn't need to know about
LangChain/ChromaDB internals directly.

This is the "R" in RAG: given a query, return the most relevant chunks
(with their source document + page) from the ward's knowledge base.
"""

from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    text: str
    source_document: str
    page: int | None = None
    score: float | None = None


async def retrieve_relevant_chunks(
    query: str,
    service_id: str | None = None,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """
    TODO:
        1. Embed `query` using the same BGE-M3 model used at ingestion time
           (see ingestion/chunk.py).
        2. Run vector similarity search in ChromaDB (retrieval/vector.py),
           optionally combined with BM25 keyword search (retrieval/bm25.py)
           via retrieval/hybrid.py.
        3. Optionally rerank the merged candidates (retrieval/reranker.py).
        4. If `service_id` is provided, filter/boost chunks whose metadata
           `service` field matches it.
        5. Return the top_k chunks as RetrievedChunk objects.

    For now this returns an empty list so the API is runnable end-to-end
    (with an empty-context answer) before the ingestion pipeline is filled in.
    """
    return []
