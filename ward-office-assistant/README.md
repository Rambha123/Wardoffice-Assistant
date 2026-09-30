# Ward Office Assistant — AI-Powered Citizen Guidance Platform

Final year project (Computer Engineering, Kathmandu University).

An AI-assisted **Citizen Guidance Platform** that combines official knowledge
retrieval (RAG), dynamic document readiness checking, personalized
administrative guidance, and ward information services — helping citizens
prepare complete applications *before* visiting the ward office, and reducing
repetitive inquiries handled by ward staff.

This is **not** a simple chatbot. See `docs/architecture.md` (to be written)
for the full system design.

## Monorepo layout

```
ward-office-assistant/
├── backend/        # FastAPI app (API, RAG orchestration, OCR, DB models)
├── frontend/        # React + Tailwind CSS SPA
├── ingestion/        # Offline pipeline: PDF -> text -> chunks -> embeddings
├── retrieval/        # Retrieval algorithms (BM25, vector, hybrid, reranker)
├── evaluation/        # RAG evaluation queries + notes
├── data/              # Raw/processed documents, extracted text, vector indexes
├── database/          # SQL schema / migrations
└── docs/              # Design docs, diagrams, meeting notes
```

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + Tailwind CSS (Vite) |
| Backend | FastAPI |
| Database | PostgreSQL |
| Auth | JWT |
| OCR | PaddleOCR |
| LLM | Gemini 2.5 Flash |
| Embeddings | BGE-M3 (local) |
| RAG framework | LangChain |
| Vector DB | ChromaDB |

## Getting started

### 1. Environment variables

```bash
cp .env.example .env
# then fill in GEMINI_API_KEY, DATABASE_URL, JWT_SECRET, etc.
```

### 2. Run everything with Docker Compose

```bash
docker-compose up --build
```

This brings up: `postgres`, `backend` (FastAPI, port 8000), `frontend` (Vite dev
server, port 5173), and `chromadb` (port 8001).

### 3. Run services individually (local dev, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 4. Ingest documents into the knowledge base

Drop Citizen Charter / forms / circular PDFs into `data/raw/`, then:

```bash
cd ingestion
python pipeline.py
```

This runs: extract → OCR (if scanned) → quality check → structure → chunk →
embed → store in ChromaDB (`data/indexes/`).

## Project status

Scaffold only — folder structure and stub files are in place so features can
be filled in incrementally: RAG service, dynamic checklist engine, document
readiness checker, admin panel, etc. See TODOs inside each file.

## Privacy note

Uploaded documents used for OCR / readiness checking are processed in memory
or in a temp directory and deleted immediately after processing. No document
images are persisted to disk or DB (see `document_readiness_service.py`).
