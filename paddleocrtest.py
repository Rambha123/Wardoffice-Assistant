"""
Quick test: OCR one page of the ward PDF using PaddleOCR.

lang="ne" is the correct code for Nepali in current PaddleOCR (there's
no separate "devanagari" code -- Nepali/Hindi/Marathi/Sanskrit all map
internally to the same Devanagari-script recognition model, but you
select it via the individual language code, e.g. "ne").

Install (first run will also download model weights, a few hundred MB,
happens automatically and only once):
    pip install paddlepaddle paddleocr pdf2image

You still need Poppler installed for pdf2image -- same poppler_path
you already got working.

Usage:
    python paddleocr_test.py works.pdf --page 1
"""

import argparse

import numpy as np
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

# Point this at wherever pdftoppm.exe lives on your machine, same as
# the tesseract script.
POPPLER_PATH = r"C:\Users\HELIOS\Downloads\Release-26.07.0-0\poppler-26.07.0\Library\bin"


def ocr_page(pdf_path: str, page_number: int, dpi: int = 300) -> str:
    images = convert_from_path(
        pdf_path, dpi=dpi, first_page=page_number, last_page=page_number,
        poppler_path=POPPLER_PATH,
    )
    page_image = images[0]

    ocr = PaddleOCR(
        lang="ne",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=True,  # handles slightly rotated/skewed pages
        enable_mkldnn=False,  # oneDNN + PIR execution has a known crash bug
                               # on CPU (NotImplementedError:
                               # ConvertPirAttribute2RuntimeAttribute).
                               # Disabling it costs some speed, not accuracy.
    )

    result = ocr.predict(np.array(page_image))

    # In the current API, each item in `result` is a dict-like object
    # with a "rec_texts" key holding the recognized lines, in reading
    # order (not yet reconstructed into table rows -- that's a later
    # parsing step).
    lines = []
    for res in result:
        lines.extend(res.get("rec_texts", []))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path")
    parser.add_argument("--page", type=int, default=1)
    args = parser.parse_args()

    text = ocr_page(args.pdf_path, args.page)
    print(f"=== PaddleOCR output (page {args.page}) ===\n")
    print(text)


if __name__ == "__main__":
    main()