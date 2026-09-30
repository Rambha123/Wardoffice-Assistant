"""
Stage A + Stage B ingestion pipeline for the Ward Citizen Charter PDF.

Stage A (extract_all_pages / parse_into_records):
    OCR every page -> reconstruct into one long text -> split into
    per-service records. Run this once per document version. Slow.

Stage B (build_chunks / index_into_chroma):
    Turn each record into a natural-language chunk + embed + store.
    Cheap to re-run whenever you change chunking or embedding logic,
    since it reads the cached JSON instead of re-running OCR.

Install:
    pip install paddlepaddle paddleocr pdf2image chromadb sentence-transformers

Usage:
    python ingest_ward_pdf.py works.pdf
    # writes data/parsed/works_records.json
    # then embeds + loads into a local ChromaDB collection
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

POPPLER_PATH = r"C:\Users\HELIOS\Downloads\Release-26.07.0-0\poppler-26.07.0\Library\bin"
OUTPUT_DIR = Path("data/parsed")

# The repeating table header that shows up on every page -- strip any
# line that closely matches this so it doesn't pollute the parsed text.
HEADER_PATTERN = re.compile(r"क\.?सं.*सेवा.*आवश्यक.*कागजात", re.IGNORECASE)

# Service rows in this document start with a number (Devanagari or
# Latin digits) followed by a service name. Adjust this pattern once
# you see real OCR output -- OCR digit recognition is imperfect, so
# you may need to loosen it.
ROW_START_PATTERN = re.compile(r"^\s*[\d१२३४५६७८९०]{1,3}\s+\S")


def extract_all_pages(pdf_path: str, dpi: int = 300) -> list[str]:
    """Stage A, part 1: OCR every page, return one text block per page.

    lang="ne" is the correct code for Nepali in current PaddleOCR --
    it maps internally to the Devanagari-script recognition model
    (there's no separate "devanagari" code to pass directly)."""
    ocr = PaddleOCR(
        lang="ne",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=True,
        enable_mkldnn=False,  # oneDNN + PIR execution has a known crash bug
                               # on CPU (NotImplementedError:
                               # ConvertPirAttribute2RuntimeAttribute).
    )
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)

    page_texts = []
    for i, image in enumerate(images, start=1):
        result = ocr.predict(np.array(image))
        lines = []
        for res in result:
            lines.extend(res.get("rec_texts", []))
        # drop repeated header lines
        lines = [ln for ln in lines if not HEADER_PATTERN.search(ln)]
        page_texts.append("\n".join(lines))
        print(f"  OCR'd page {i}/{len(images)}")
    return page_texts


def parse_into_records(page_texts: list[str]) -> list[dict]:
    """Stage A, part 2: turn OCR'd lines into one record per service row.

    NOTE: this is a first-pass heuristic splitter, not a finished
    parser. Government table OCR is messy -- run this, inspect the
    output JSON, and tighten ROW_START_PATTERN / the field-splitting
    logic below against what you actually see. Treat this as a
    starting point to iterate on, not a finished component.
    """
    full_text = "\n".join(page_texts)
    lines = [ln for ln in full_text.split("\n") if ln.strip()]

    records = []
    current = None
    for line in lines:
        if ROW_START_PATTERN.match(line):
            if current:
                records.append(current)
            parts = line.split(maxsplit=1)
            current = {
                "service_number": parts[0],
                "service_name": parts[1] if len(parts) > 1 else "",
                "raw_text": line,
            }
        elif current:
            current["raw_text"] += "\n" + line

    if current:
        records.append(current)

    return records


def build_chunk_text(record: dict) -> str:
    """Stage B, part 1: turn a structured record into the text that
    actually gets embedded. Keep this human-readable -- it's also
    what an LLM will see as retrieved context."""
    return (
        f"Service: {record['service_name']} (Service No. {record['service_number']})\n"
        f"{record['raw_text']}"
    )


def index_into_chroma(records: list[dict], collection_name: str = "ward_services"):
    """Stage B, part 2: embed each record and store it. Swap in your
    actual BGE-M3 embedding call here -- this stub uses ChromaDB's
    default embedding function just to prove the pipeline end-to-end;
    replace it before you rely on retrieval quality."""
    import chromadb

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(collection_name)

    ids = [f"service-{r['service_number']}-{i}" for i, r in enumerate(records)]
    documents = [build_chunk_text(r) for r in records]
    metadatas = [
        {"service_number": r["service_number"], "service_name": r["service_name"]}
        for r in records
    ]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Indexed {len(records)} records into ChromaDB collection '{collection_name}'.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path")
    parser.add_argument("--skip-ocr", action="store_true",
                         help="reuse the cached JSON instead of re-running OCR")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"{Path(args.pdf_path).stem}_records.json"

    if args.skip_ocr and json_path.exists():
        print(f"Loading cached records from {json_path}")
        records = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        print("Running OCR on all pages (this is the slow part)...")
        page_texts = extract_all_pages(args.pdf_path)
        records = parse_into_records(page_texts)
        json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved {len(records)} parsed records to {json_path}")

    index_into_chroma(records)


if __name__ == "__main__":
    main()