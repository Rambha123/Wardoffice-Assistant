"""
Compare two ways of pulling text out of the ward Citizen Charter PDF:

  1. RAW TEXT EXTRACTION  -- reads the PDF's embedded text layer directly.
     Fast, but breaks on this file because of how the Devanagari font
     (Kalimati, Identity-H encoding) is embedded.

  2. RENDER + OCR         -- renders each page to an image, then runs OCR
     (Tesseract with the Nepali model here; swap in PaddleOCR for the
     real pipeline) on the image. Slower, but reads what's actually on
     the page instead of trusting the broken text layer.

Install requirements (Ubuntu/Debian):
    sudo apt-get install -y tesseract-ocr tesseract-ocr-nep poppler-utils
    pip install pymupdf pdf2image pytesseract --break-system-packages

Usage:
    python extraction_comparison.py path/to/works.pdf --page 1
"""

import argparse
import sys

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import pytesseract 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_raw_text(pdf_path: str, page_number: int) -> str:
    """Method 1: pull the embedded text layer directly. Fast, but only
    trustworthy if the PDF's font encoding is standard."""
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    return page.get_text()


def extract_via_ocr(pdf_path: str, page_number: int, dpi: int = 300) -> str:
    """Method 2: render the page to an image, then OCR it. Slower, but
    reads the actual glyphs on the page rather than the (possibly
    broken) internal character codes."""
    images = convert_from_path(
    pdf_path, dpi=dpi, first_page=page_number, last_page=page_number,
    poppler_path=r"C:\Users\HELIOS\Downloads\Release-26.07.0-0\poppler-26.07.0\Library\bin"
)
    page_image = images[0]
    # lang="nep" requires tesseract-ocr-nep to be installed.
    # --psm 6 = "assume a single uniform block of text", works reasonably
    # well for this document's dense table layout.
    text = pytesseract.image_to_string(page_image, lang="nep", config="--psm 6")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--page", type=int, default=1, help="1-indexed page number to test (default: 1)"
    )
    args = parser.parse_args()

    print(f"=== Method 1: Raw text extraction (page {args.page}) ===\n")
    try:
        raw = extract_raw_text(args.pdf_path, args.page)
        print(raw[:1500])
    except Exception as e:
        print(f"Raw extraction failed: {e}", file=sys.stderr)

    print(f"\n=== Method 2: Render + OCR (page {args.page}) ===\n")
    try:
        ocr_text = extract_via_ocr(args.pdf_path, args.page)
        print(ocr_text[:1500])
    except Exception as e:
        print(f"OCR extraction failed: {e}", file=sys.stderr)

    print(
        "\n--- Compare the two blocks above. If Method 1 looks garbled "
        "(broken conjuncts, stray '?' characters, jumbled word order) "
        "while Method 2 reads as clean Devanagari, your PDF has the same "
        "font-encoding issue described in the write-up: route this "
        "document (and any others that show the same symptom) through "
        "OCR instead of direct text extraction, even though it's a "
        "born-digital PDF, not a scan. ---"
    )


if __name__ == "__main__":
    main()