"""
Vector similarity search against ChromaDB, using BGE-M3 embeddings
(the same model used at ingestion time in ingestion/chunk.py — keeping
these in sync is critical, a mismatched embedding model silently breaks
retrieval quality).
"""

import chromadb

# TODO: `backend/` and `retrieval/` are currently separate top-level
# packages, so settings can't be imported directly yet. Either:
#   (a) move retrieval/ inside backend/app/ once its interface stabilizes, or
#   (b) install backend as an editable package so `from app.core.config
#       import settings` works from here too.
# For now, hardcode or pass persist_dir/collection_name as arguments.

CHROMA_PERSIST_DIR = "../data/indexes"
CHROMA_COLLECTION_NAME = "ward_knowledge_base"


def get_client() -> "chromadb.PersistentClient":
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)


def upsert(chunks: list, vectors: list[list[float]]):
    """
    chunks: list of ingestion.chunk.Chunk objects.
    TODO:
        collection = get_collection()
        collection.upsert(
            ids=[f"{c.metadata['source']}-{i}" for i, c in enumerate(chunks)],
            embeddings=vectors,
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )
    """
    raise NotImplementedError


def similarity_search(query_embedding: list[float], top_k: int = 10, where: dict | None = None):
    """
    TODO:
        collection = get_collection()
        return collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where)
    """
    raise NotImplementedError
