"""
RAG orchestration: takes a citizen's question, retrieves relevant chunks
(via retrieval_service), builds a grounded prompt, and calls the LLM
(via llm_service) to produce the final answer.

Pipeline:
    question -> retrieval_service.retrieve_relevant_chunks()
             -> build grounded prompt (chunks + question)
             -> llm_service.generate_answer()
             -> ChatResponse (answer + cited sources)

Design notes:
    - Gemini NEVER sees the full Citizen Charter PDFs, only the top-k
      retrieved chunks, so answers stay grounded in official documents.
    - The prompt should instruct Gemini to answer ONLY from the provided
      context and to reply in the same language the question was asked in
      (English / Nepali / mixed).
"""

from app.schemas.chat import ChatResponse, SourceChunk
from app.services import retrieval_service, llm_service

SYSTEM_PROMPT_TEMPLATE = """You are the AI Service Assistant for a ward office in Nepal.
Answer the citizen's question using ONLY the context below, which is extracted
from official Citizen Charters, forms, and circulars. If the answer is not
in the context, say you don't have that information and suggest contacting
the ward office directly. Reply in the same language as the question
(English, Nepali, or a mix of both).

Context:
{context}

Question: {question}
"""


async def answer_question(
    question: str,
    session_id: str | None = None,
    service_id: str | None = None,
) -> ChatResponse:
    # 1. Retrieve relevant chunks (hybrid: BM25 + vector, see retrieval_service).
    retrieved = await retrieval_service.retrieve_relevant_chunks(
        query=question, service_id=service_id, top_k=5
    )

    # 2. Build the grounded prompt.
    context_text = "\n\n---\n\n".join(chunk.text for chunk in retrieved)
    prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text, question=question)

    # 3. Call Gemini.
    answer_text = await llm_service.generate_answer(prompt)

    return ChatResponse(
        answer=answer_text,
        sources=[
            SourceChunk(text=c.text, source_document=c.source_document, page=c.page)
            for c in retrieved
        ],
        detected_language=None,  # TODO: run/attach a lightweight language detector
    )


# TODO: session_id -> persist last N turns (Postgres or in-memory dict for the
# prototype) so the assistant can handle short follow-ups like "and the fee?".
