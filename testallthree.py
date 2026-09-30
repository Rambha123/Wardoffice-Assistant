"""
Compare raw PDF text vs PaddleOCR on a ward Citizen Charter page.
Works around PaddlePaddle 3.3.x oneDNN crash on Windows.
"""

import os

# MUST be set before importing paddle / paddleocr
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"

import argparse
import sys
from pathlib import Path


def extract_raw_text(pdf_path: str, page_number: int) -> str:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    try:
        page = doc[page_number - 1]
        return page.get_text() or ""
    finally:
        doc.close()


def render_page_pymupdf(pdf_path: str, page_number: int, dpi: int = 300):
    import pymupdf
    from PIL import Image

    doc = pymupdf.open(pdf_path)
    try:
        page = doc[page_number - 1]
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()


def extract_via_paddle(pdf_path: str, page_number: int, dpi: int = 300) -> str:
    import numpy as np
    from paddleocr import PaddleOCR  # import HERE, after env vars above

    page_image = render_page_pymupdf(pdf_path, page_number, dpi=dpi)
    img = np.array(page_image.convert("RGB"))

    ocr = PaddleOCR(
        lang="ne",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=True,
        enable_mkldnn=False,
    )

    lines = []

    # PaddleOCR 3.x
    if hasattr(ocr, "predict"):
        result = ocr.predict(img)
        for item in (result if isinstance(result, list) else [result]):
            texts = getattr(item, "rec_texts", None)
            if texts is None and isinstance(item, dict):
                data = item.get("res", item)
                texts = data.get("rec_texts") or data.get("texts")
            if texts:
                for t in texts:
                    if t and str(t).strip():
                        lines.append(str(t).strip())
        if lines:
            return "\n".join(lines)

    # PaddleOCR 2.x fallback
    try:
        result = ocr.ocr(img, cls=True)
    except TypeError:
        result = ocr.ocr(img)

    if result:
        for page in result:
            if not page:
                continue
            for line in page:
                try:
                    t = line[1][0]
                    if t and str(t).strip():
                        lines.append(str(t).strip())
                except (IndexError, TypeError):
                    continue

    return "\n".join(lines)


def preview(text: str, limit: int = 1500) -> str:
    text = (text or "").strip()
    if not text:
        return "(empty)"
    return text if len(text) <= limit else text[:limit] + "\n… [truncated]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--methods", default="raw,paddle")
    args = parser.parse_args()

    if not Path(args.pdf_path).is_file():
        print(f"File not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    methods = {m.strip().lower() for m in args.methods.split(",")}

    if "raw" in methods:
        print(f"=== Method 1: Raw text extraction (page {args.page}) ===\n")
        try:
            raw = extract_raw_text(args.pdf_path, args.page)
            print(preview(raw))
            print(f"\n[raw chars: {len(raw)}]")
        except Exception as e:
            print(f"Raw extraction failed: {e}", file=sys.stderr)

    if "paddle" in methods:
        print(
            f"\n=== Method 3: Render + PaddleOCR "
            f"(page {args.page}, dpi={args.dpi}) ===\n"
        )
        try:
            paddle_text = extract_via_paddle(args.pdf_path, args.page, dpi=args.dpi)
            print(preview(paddle_text))
            print(f"\n[paddle chars: {len(paddle_text)}]")
        except Exception as e:
            print(f"PaddleOCR extraction failed: {e}", file=sys.stderr)
            print(
                "If this is still the oneDNN/PIR error, run:\n"
                '  pip install paddlepaddle==3.2.0 "paddleocr>=3.3.0,<3.4.0"',
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()