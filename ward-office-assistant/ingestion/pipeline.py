"""
Orchestrates the full offline ingestion pipeline:

    data/raw/*.pdf
        -> extract.py   (text layer; flags empty/scanned pages)
        -> ocr.py        (fills in text for scanned pages)
        -> quality.py    (fail fast on garbled/too-short documents)
        -> structure.py  (recover headings / service boundaries)
        -> chunk.py      (split + embed with BGE-M3)
        -> ChromaDB      (persisted to data/indexes/, via retrieval/vector.py)

Run this whenever new Citizen Charters / forms / circulars are dropped into
data/raw/, or automatically after an admin-panel upload
(see backend/app/api/routes/documents.py -> admin_upload_knowledge_document).
"""

from pathlib import Path

import extract
import ocr
import quality
import structure
import chunk

RAW_DIR = Path("../data/raw")


def run_pipeline():
    for pdf_path in RAW_DIR.glob("*.pdf"):
        print(f"\n=== Processing {pdf_path.name} ===")

        # TODO: wire these together once each module's functions are implemented:
        # 1. pages = extract.extract_text_from_pdf(pdf_path)
        # 2. empty_pages = [i for i, p in enumerate(pages) if extract.is_page_empty(p)]
        # 3. if empty_pages: ocr.run(pdf_path, empty_pages)  # fills gaps
        # 4. full_text = "\n\n".join(pages)
        # 5. report = quality.check_text_quality(pdf_path.name, full_text)
        #    if not report.passed: print(report.issues); continue
        # 6. sections = structure.detect_sections(full_text)
        # 7. chunks = [c for s in sections for c in chunk.split_section(s, pdf_path.name)]
        # 8. vectors = chunk.embed_chunks(chunks)
        # 9. retrieval.vector.upsert(chunks, vectors)   # push into ChromaDB

        print("Pipeline steps are stubbed — implement TODOs above as each module fills in.")


if __name__ == "__main__":
    run_pipeline()
