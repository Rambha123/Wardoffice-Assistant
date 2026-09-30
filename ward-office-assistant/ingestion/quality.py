"""
Step 2 of ingestion: sanity-check extracted text before it goes into the
knowledge base. Bad ingestion (garbled OCR, near-empty docs) silently
poisons every downstream answer, so this step is worth taking seriously.

Checks to implement:
    - Minimum length per document / per page.
    - Garbage-character ratio (OCR gone wrong: lots of symbols/mojibake).
    - Duplicate-page detection (headers/footers repeated everywhere).
    - Language sanity check (expect English/Nepali; flag anything else).
"""

from dataclasses import dataclass


@dataclass
class QualityReport:
    document_name: str
    passed: bool
    issues: list[str]


def check_text_quality(document_name: str, text: str) -> QualityReport:
    issues: list[str] = []

    if len(text.strip()) < 100:
        issues.append("Document text is suspiciously short (<100 chars).")

    # TODO: garbage-character ratio check, e.g.:
    # non_alnum_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / max(len(text), 1)
    # if non_alnum_ratio > 0.3: issues.append("High ratio of non-alphanumeric characters.")

    return QualityReport(document_name=document_name, passed=not issues, issues=issues)


if __name__ == "__main__":
    # TODO: iterate data/extracted/{raw_text,ocr_text}/*.txt and print a
    # summary report; fail loudly (non-zero exit) on any document that
    # doesn't pass, so pipeline.py can stop before bad data hits ChromaDB.
    pass
