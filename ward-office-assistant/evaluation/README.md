# Evaluation

Manual/semi-automated RAG quality checks, separate from the `backend/tests/`
unit tests (which test code correctness, not answer quality).

## `queries.json`

A set of representative citizen questions across services and languages
(English / Nepali / mixed), each with notes on what a correct answer should
contain once real documents are ingested.

## Suggested workflow

1. Ingest real Citizen Charter / form / circular PDFs (`ingestion/pipeline.py`).
2. For each entry in `queries.json`, call `POST /api/chat/` with the question.
3. Manually score each answer (or, once there's a large enough query set,
   write a small script that checks whether `expected_answer_contains`
   substrings appear in the answer / retrieved sources).
4. Track metrics over time as chunking/retrieval parameters change:
   - **Retrieval hit rate**: did the correct document/page get retrieved at all?
   - **Answer correctness**: manually judged, or substring-matched.
   - **Groundedness**: does the answer avoid claiming things not present in
     any retrieved chunk (no hallucinated fees/procedures)?

## TODO

- [ ] Write `run_eval.py` once the chat endpoint is functional end-to-end.
- [ ] Expand `queries.json` after the ward provides real Citizen Charter PDFs
      (add fee/procedure "ground truth" so mismatches are easy to spot).
- [ ] Consider a simple retrieval-only eval (precision@k) that doesn't
      depend on Gemini API calls, for faster iteration on chunking/retrieval.
