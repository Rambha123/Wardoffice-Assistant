"""
Step 1 of ingestion: extract raw text from source PDFs in data/raw/.

Uses a text-layer extractor (e.g. pypdf/pdfplumber) first; pages that come
back empty (scanned/image-only pages) are handed off to ocr.py instead.
"""

from pathlib import Path

RAW_DIR = Path("../data/raw")
OUTPUT_DIR = Path("../data/extracted/raw_text")


def extract_text_from_pdf(pdf_path: Path) -> list[str]:
    """
    Returns a list of per-page text strings.

    TODO: implement with pdfplumber or pypdf, e.g.:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return [page.extract_text() or "" for page in pdf.pages]
    """
    raise NotImplementedError


def is_page_empty(page_text: str, min_chars: int = 20) -> bool:
    """Heuristic: pages with almost no extracted text are likely scanned images."""
    return len(page_text.strip()) < min_chars


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for pdf_path in RAW_DIR.glob("*.pdf"):
        pages = extract_text_from_pdf(pdf_path)
        # TODO: for pages where is_page_empty() is True, flag them for
        # ocr.py instead of writing empty text here.
        out_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"
        out_path.write_text("\n\n".join(pages), encoding="utf-8")
        print(f"Extracted {pdf_path.name} -> {out_path.name}")


if __name__ == "__main__":
    run()
