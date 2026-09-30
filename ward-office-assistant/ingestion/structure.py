"""
Step 3 of ingestion: recover document structure from raw extracted text
before chunking — section headings, service boundaries within a Citizen
Charter, tables of fees, etc. Chunking blindly by character count tends to
split a fee table or a document-requirement list mid-way, which hurts
retrieval quality later.

This is one of the "advanced, beyond a basic RAG system" pieces the
supervisor asked for: structure-aware chunking rather than naive fixed-size
splitting.
"""

from dataclasses import dataclass


@dataclass
class StructuredSection:
    heading: str | None
    text: str
    service_name: str | None = None  # e.g. "Birth Registration", if detectable


def detect_sections(raw_text: str) -> list[StructuredSection]:
    """
    TODO: implement heading detection. Options, roughly in order of effort:
        1. Regex heuristics: numbered headings ("1.", "1.1"), ALL CAPS lines,
           lines ending without a period followed by a blank line, etc.
        2. Layout-aware extraction (pdfplumber word positions / font size)
           if extract.py is upgraded to keep layout metadata.
        3. LLM-assisted structuring: ask Gemini to segment + label a page's
           text into sections (slower/costlier, use as a fallback).
    """
    return [StructuredSection(heading=None, text=raw_text)]


if __name__ == "__main__":
    pass
