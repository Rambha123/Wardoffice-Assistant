"""
ward_table_extractor.py

Layout-aware extraction pipeline for Nepali ward-office "Citizen Charter"
PDFs (नागरिक बडापत्र), designed for feeding a RAG index.

WHY THIS EXISTS
----------------
Raw text extraction (page.get_text()) breaks on these PDFs because the
Devanagari font is embedded with Identity-H encoding that PyMuPDF/pdfplumber
can't map back to correct glyphs. Running OCR on the whole page ("--psm 6")
avoids the encoding problem but introduces a NEW problem: reading order.
Tesseract reads left-to-right across the page, so when a table cell wraps
across many lines (e.g. a long list of required documents), OCR output ends
up interleaving text from column 2, 3, and 4 instead of respecting the
table's actual columns and rows.

The fix used here: the table's grid lines are vector graphics baked into
the PDF (not raster pixels), so they survive perfectly even though the text
encoding doesn't. We extract precise cell bounding boxes from those vector
lines, then OCR each cell as its own small image. This gives clean,
correctly-ordered per-cell text with no cross-column bleeding.

We then:
  1. Forward-fill merged/spanned cells (e.g. "जिम्मेवार व्यक्ति" spanning
     multiple visual rows for one service).
  2. Detect "continuation" tables -- ward charter PDFs often split one
     service's document list across a page break, re-drawing the header
     row on the next page with no new serial number in column 1 -- and
     merge them back into the previous table's last open row.
  3. Serialize each logical row (= one service) into a small structured
     text chunk, ready to embed for RAG. One row -> one chunk, so a query
     like "birth registration documents" retrieves one complete, coherent
     record instead of a fragment of a column.

INSTALL (Ubuntu/Debian)
------------------------
    sudo apt-get install -y tesseract-ocr tesseract-ocr-nep poppler-utils
    pip install pymupdf pdfplumber pytesseract pillow --break-system-packages

USAGE
-----
    python ward_table_extractor.py path/to/charter.pdf --out chunks.json

    # Inspect a single page's detected grid before trusting the OCR pass:
    python ward_table_extractor.py path/to/charter.pdf --debug-page 1
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import dataclass, field
from typing import Optional

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OCR_LANG = "nep"
OCR_DPI = 400
MULTILINE_PSM = "6"   # block of text, for wrapped cells (document lists)
SINGLELINE_PSM = "7"  # single line, for short cells (fees, service names)

# Column headers as they appear in these ward charter tables. Used to
# detect a repeated header row (== a continuation table on a new page).
EXPECTED_HEADERS = ["क.सं", "सेवा", "आवश्यक", "शुल्क", "समय", "जिम्मेवार"]

# Heuristic: a cell counts as "short" (use single-line PSM) if its
# rendered height is below this many points -- long document lists
# and multi-line cells are much taller than this.
SHORT_CELL_HEIGHT_PT = 40


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TableGrid:
    page_number: int
    header: list[str]
    rows: list[list[Optional[tuple]]]  # each cell: bbox tuple or None (merged/spanned)


@dataclass
class LogicalRow:
    """One reassembled, semantically complete row (= one service)."""
    cells: dict[str, str] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not any(v.strip() for v in self.cells.values())


# ---------------------------------------------------------------------------
# Step 1: pull table grid geometry from vector lines (no OCR yet)
# ---------------------------------------------------------------------------

def get_page_tables(pdf_path: str, page_number: int) -> list:
    """Return pdfplumber Table objects found via vector line detection."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number - 1]
        settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_tolerance": 5,
        }
        return page.find_tables(table_settings=settings)


def table_cell_bboxes(table) -> list[list[Optional[tuple]]]:
    """
    pdfplumber gives a flat list of cell bboxes per row via table.rows,
    where a spanned-over cell shows up as None. We just pass that through;
    forward-filling happens later once we have OCR'd text.
    """
    grid = []
    for row in table.rows:
        grid.append(list(row.cells))
    return grid


# ---------------------------------------------------------------------------
# Step 2: render + OCR each cell individually
# ---------------------------------------------------------------------------

def render_cell(doc: fitz.Document, page_number: int, bbox: tuple, dpi: int = OCR_DPI) -> Image.Image:
    page = doc[page_number - 1]
    x0, top, x1, bottom = bbox
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    clip = fitz.Rect(x0, top, x1, bottom)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    return Image.open(io.BytesIO(pix.tobytes("png")))


def ocr_cell(img: Image.Image, bbox: tuple) -> str:
    x0, top, x1, bottom = bbox
    height_pt = bottom - top
    psm = SINGLELINE_PSM if height_pt < SHORT_CELL_HEIGHT_PT else MULTILINE_PSM
    text = pytesseract.image_to_string(img, lang=OCR_LANG, config=f"--psm {psm}")
    return text.strip()


def ocr_table(pdf_path: str, page_number: int, table) -> list[list[str]]:
    doc = fitz.open(pdf_path)
    grid = table_cell_bboxes(table)
    text_grid: list[list[str]] = []
    for row in grid:
        text_row = []
        for bbox in row:
            if bbox is None:
                text_row.append(None)  # mark as spanned, filled in later
                continue
            img = render_cell(doc, page_number, bbox)
            text_row.append(ocr_cell(img, bbox))
        text_grid.append(text_row)
    doc.close()
    return text_grid


# ---------------------------------------------------------------------------
# Step 3: forward-fill merged/spanned cells
# ---------------------------------------------------------------------------

def forward_fill(text_grid: list[list[str]]) -> list[list[str]]:
    """
    A None entry means pdfplumber found no distinct cell there -- i.e. it's
    part of a merge/span from the row above in that column. Carry the
    value down. First row can't be filled from above; leave blank.
    """
    if not text_grid:
        return text_grid
    n_cols = max(len(r) for r in text_grid)
    filled = [row[:] + [None] * (n_cols - len(row)) for row in text_grid]
    for col in range(n_cols):
        last_value = ""
        for row in filled:
            if row[col] is None:
                row[col] = last_value
            else:
                last_value = row[col]
    return filled


# ---------------------------------------------------------------------------
# Step 4: detect + merge continuation tables across page breaks
# ---------------------------------------------------------------------------

def looks_like_header_row(row: list[str]) -> bool:
    joined = " ".join(row)
    hits = sum(1 for h in EXPECTED_HEADERS if h in joined)
    return hits >= 3


def is_continuation_table(text_grid: list[list[str]]) -> bool:
    """
    A continuation table starts with the same header row repeated, and its
    first data row's serial-number column (क.सं.) is blank -- i.e. it's
    still describing the previous page's last service.
    """
    if len(text_grid) < 2:
        return False
    if not looks_like_header_row(text_grid[0]):
        return False
    first_data_row = text_grid[1]
    serial_cell = (first_data_row[0] or "").strip()
    return serial_cell == ""


def merge_continuation(base_rows: list[list[str]], cont_rows: list[list[str]]) -> list[list[str]]:
    """
    Append the continuation table's data rows (skipping its repeated
    header) onto base_rows, concatenating into the last existing row
    where columns match, since it's the same service continuing.
    """
    cont_data_rows = cont_rows[1:]  # drop repeated header
    if not base_rows:
        return cont_data_rows

    last_row = base_rows[-1]
    for cont_row in cont_data_rows:
        for col_idx, value in enumerate(cont_row):
            if col_idx >= len(last_row):
                continue
            addition = (value or "").strip()
            if not addition:
                continue
            if last_row[col_idx].strip():
                last_row[col_idx] = last_row[col_idx].rstrip() + "\n" + addition
            else:
                last_row[col_idx] = addition
    return base_rows


# ---------------------------------------------------------------------------
# Step 5: full-document pipeline
# ---------------------------------------------------------------------------

def extract_all_rows(pdf_path: str) -> list[list[str]]:
    """
    Walk every page, OCR every detected table, forward-fill merges, and
    stitch continuation tables back onto the previous page's open row.
    Returns one flat list of fully-formed data rows (header rows dropped).
    """
    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)

    all_rows: list[list[str]] = []
    header: Optional[list[str]] = None

    for page_number in range(1, n_pages + 1):
        tables = get_page_tables(pdf_path, page_number)
        for table in tables:
            raw_grid = ocr_table(pdf_path, page_number, table)
            filled_grid = forward_fill(raw_grid)

            if is_continuation_table(filled_grid):
                all_rows = merge_continuation(all_rows, filled_grid)
                continue

            if looks_like_header_row(filled_grid[0]):
                header = filled_grid[0]
                data_rows = filled_grid[1:]
            else:
                data_rows = filled_grid

            all_rows.extend(data_rows)

    return all_rows, header


# ---------------------------------------------------------------------------
# Step 6: chunk each row into a RAG-ready text record
# ---------------------------------------------------------------------------

DEFAULT_COLUMN_NAMES = [
    "क्र.सं.",
    "सेवा",
    "आवश्यक कागजातहरू",
    "सेवा शुल्क तथा दस्तुर रकम रुपैयामा",
    "लाग्ने समय",
    "जिम्मेवार व्यक्ति",
]


def row_to_chunk(row: list[str], column_names: list[str]) -> dict:
    """Turn one logical row into a dict + a serialized text block for embedding."""
    named = {}
    for i, col_name in enumerate(column_names):
        named[col_name] = row[i].strip() if i < len(row) else ""

    text = (
        f"सेवा: {named.get('सेवा', '')}\n"
        f"आवश्यक कागजातहरू:\n{named.get('आवश्यक कागजातहरू', '')}\n"
        f"सेवा शुल्क: {named.get('सेवा शुल्क तथा दस्तुर रकम रुपैयामा', '')}\n"
        f"लाग्ने समय: {named.get('लाग्ने समय', '')}\n"
        f"जिम्मेवार व्यक्ति: {named.get('जिम्मेवार व्यक्ति', '')}"
    )
    return {"fields": named, "chunk_text": text}


def build_chunks(pdf_path: str) -> list[dict]:
    rows, header = extract_all_rows(pdf_path)
    column_names = header if header and len(header) >= len(DEFAULT_COLUMN_NAMES) else DEFAULT_COLUMN_NAMES
    chunks = []
    for row in rows:
        # skip fully blank rows (can happen from stray table detections)
        if not any((cell or "").strip() for cell in row):
            continue
        chunks.append(row_to_chunk(row, column_names))
    return chunks


# ---------------------------------------------------------------------------
# Debug helper: visualize detected grid for one page before trusting OCR
# ---------------------------------------------------------------------------

def debug_page(pdf_path: str, page_number: int, out_path: str = "debug_page.png"):
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    tables = get_page_tables(pdf_path, page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    for table in tables:
        for row in table.rows:
            for bbox in row.cells:
                if bbox is None:
                    continue
                x0, top, x1, bottom = [c * 2 for c in bbox]
                draw.rectangle([x0, top, x1, bottom], outline="red", width=2)
    img.save(out_path)
    print(f"Saved grid overlay to {out_path} -- check that every cell has a red box "
          f"and no two service rows share a box before trusting the OCR pass.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf_path", help="Path to the ward charter PDF")
    parser.add_argument("--out", default="chunks.json", help="Output JSON file of RAG chunks")
    parser.add_argument("--debug-page", type=int, help="Render a grid overlay for one page and exit")
    args = parser.parse_args()

    if args.debug_page:
        debug_page(args.pdf_path, args.debug_page)
        return

    chunks = build_chunks(args.pdf_path)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(chunks)} row-level chunks -> {args.out}")
    for c in chunks[:2]:
        print("\n---")
        print(c["chunk_text"])


if __name__ == "__main__":
    main()