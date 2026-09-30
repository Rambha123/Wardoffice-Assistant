"""
Step 1b of ingestion (fallback): OCR scanned/image-only PDF pages that
extract.py couldn't get text from directly.

Reuses PaddleOCR, same engine as backend/app/services/ocr_service.py but
run offline/in batch here rather than per-request. Consider factoring the
PaddleOCR engine setup into a shared module if duplication becomes painful.
"""

from pathlib import Path

OUTPUT_DIR = Path("../data/extracted/ocr_text")


def ocr_pdf_page(pdf_path: Path, page_number: int) -> str:
    """
    TODO:
        1. Rasterize the page to an image (e.g. via pdf2image / pymupdf).
        2. Run PaddleOCR on the image.
        3. Return the concatenated recognized text.
    """
    raise NotImplementedError


def run(pdf_path: Path, empty_page_numbers: list[int]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    texts = [ocr_pdf_page(pdf_path, n) for n in empty_page_numbers]
    out_path = OUTPUT_DIR / f"{pdf_path.stem}_ocr.txt"
    out_path.write_text("\n\n".join(texts), encoding="utf-8")
    print(f"OCR'd {len(empty_page_numbers)} pages of {pdf_path.name} -> {out_path.name}")


if __name__ == "__main__":
    # TODO: called by pipeline.py with the list of empty pages found by extract.py
    pass
