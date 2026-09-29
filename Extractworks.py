
import io
import json
import re

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image, ImageOps

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_PATH = "works.pdf"
OCR_LANG = "nep+eng"
DPI = 400
COLUMN_NAMES = [
    "क्र.सं.",
    "सेवा",
    "आवश्यक कागजातहरू",
    "सेवा शुल्क तथा दस्तुर रकम रुपैयामा",
    "लाग्ने समय",
    "जिम्मेवार व्यक्ति",
]


def render_cell(doc, page_idx, bbox, dpi=DPI):
    page = doc[page_idx]
    x0, top, x1, bottom = bbox
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    clip = fitz.Rect(x0, top, x1, bottom)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    return Image.open(io.BytesIO(pix.tobytes("png")))


def autocrop_to_ink(img, inset=8, thresh=40, pad=15):
    """Trim the cell's grid-line border, then crop tightly to the actual
    dark pixels so sparse cells (a lone serial number in a tall cell)
    don't get lost in surrounding whitespace during OCR."""
    gray = img.convert("L")
    w, h = gray.size
    if w <= 2 * inset or h <= 2 * inset:
        return gray
    inner = gray.crop((inset, inset, w - inset, h - inset))
    inv = ImageOps.invert(inner)
    bw = inv.point(lambda p: 255 if p > thresh else 0)
    bbox = bw.getbbox()
    if not bbox:
        return None  # cell is genuinely blank
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(inner.width, x1 + pad)
    y1 = min(inner.height, y1 + pad)
    return inner.crop((x0, y0, x1, y1))


def ocr_cell(img):
    cropped = autocrop_to_ink(img)
    if cropped is None:
        return ""
    text = pytesseract.image_to_string(cropped, lang=OCR_LANG, config="--psm 6")
    return text.strip()


def clean_text(t: str) -> str:
    # collapse the blank lines Tesseract leaves between wrapped lines
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    return "\n".join(lines)


def extract_all_rows():
    doc = fitz.open(PDF_PATH)
    all_rows = []  # list of dict(col_name -> text)

    with pdfplumber.open(PDF_PATH) as pdf:
        n_pages = len(pdf.pages)
        for page_idx in range(n_pages):
            page = pdf.pages[page_idx]
            tables = page.find_tables(
                table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )
            if not tables:
                continue
            table = tables[0]
            data_rows = table.rows[1:]  # row 0 is the repeated header

            for row in data_rows:
                cell_texts = []
                for bbox in row.cells:
                    if bbox is None:
                        cell_texts.append("")
                        continue
                    img = render_cell(doc, page_idx, bbox)
                    cell_texts.append(clean_text(ocr_cell(img)))

                serial = cell_texts[0].strip()
                service = cell_texts[1].strip()

                if serial or service:
                    # new service starts here
                    all_rows.append({
                        COLUMN_NAMES[i]: cell_texts[i] for i in range(len(COLUMN_NAMES))
                    })
                else:
                    if not all_rows:
                        continue
                    last = all_rows[-1]
                    for i, col_name in enumerate(COLUMN_NAMES):
                        addition = cell_texts[i].strip()
                        if not addition:
                            continue
                        if last[col_name].strip():
                            last[col_name] = last[col_name].rstrip() + "\n" + addition
                        else:
                            last[col_name] = addition

            print(f"page {page_idx + 1}/{n_pages} done, {len(all_rows)} services so far", flush=True)

    doc.close()
    return all_rows


def row_to_chunk(row: dict) -> dict:
    text = (
        f"सेवा: {row.get('सेवा', '')}\n"
        f"आवश्यक कागजातहरू:\n{row.get('आवश्यक कागजातहरू', '')}\n"
        f"सेवा शुल्क: {row.get('सेवा शुल्क तथा दस्तुर रकम रुपैयामा', '')}\n"
        f"लाग्ने समय: {row.get('लाग्ने समय', '')}\n"
        f"जिम्मेवार व्यक्ति: {row.get('जिम्मेवार व्यक्ति', '')}"
    )
    return {"fields": row, "chunk_text": text}


NEPALI_DIGITS = "०१२३४५६७८९"


def to_nepali_numeral(n: int) -> str:
    return "".join(NEPALI_DIGITS[int(d)] for d in str(n))


if __name__ == "__main__":
    rows = extract_all_rows()
    for i, row in enumerate(rows, start=1):
        row["क्र.सं."] = to_nepali_numeral(i)

    chunks = [row_to_chunk(r) for r in rows]
    with open("works_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"\nExtracted {len(chunks)} services -> works_chunks.json")