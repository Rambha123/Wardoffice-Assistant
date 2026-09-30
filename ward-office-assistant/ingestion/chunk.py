"""
Step 4 of ingestion: split structured sections into embedding-sized chunks,
embed them with BGE-M3, and prepare records for ChromaDB.

Each ChromaDB record stores:
    - embedding vector
    - original chunk text
    - metadata: {source, page, service, file_name}
"""

from dataclasses import dataclass, field

from structure import StructuredSection

CHUNK_SIZE_CHARS = 800
CHUNK_OVERLAP_CHARS = 150


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


def split_section(section: StructuredSection, source_file: str, page: int | None = None) -> list[Chunk]:
    """
    TODO: use LangChain's RecursiveCharacterTextSplitter (or a hand-rolled
    sliding window) with CHUNK_SIZE_CHARS / CHUNK_OVERLAP_CHARS, e.g.:

        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_CHARS, chunk_overlap=CHUNK_OVERLAP_CHARS
        )
        pieces = splitter.split_text(section.text)

    Then wrap each piece as a Chunk with metadata:
        {"source": source_file, "page": page, "service": section.service_name}
    """
    return [Chunk(text=section.text, metadata={"source": source_file, "page": page, "service": section.service_name})]


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """
    TODO: load BGE-M3 via sentence-transformers and embed chunk texts, e.g.:

        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-m3")
        return model.encode([c.text for c in chunks], normalize_embeddings=True).tolist()
    """
    raise NotImplementedError


if __name__ == "__main__":
    pass
