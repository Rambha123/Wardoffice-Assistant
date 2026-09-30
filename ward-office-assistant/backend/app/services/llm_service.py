"""
Thin wrapper around the Gemini API (google-generativeai SDK). Keeping all
Gemini calls in one place makes it easy to swap models, add retries, or
add function/tool calling later without touching rag_service.py.
"""

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)


async def generate_answer(prompt: str) -> str:
    """
    Sends `prompt` (already grounded with retrieved context) to Gemini and
    returns the plain-text answer.

    TODO:
        - Add retry/backoff (tenacity) for transient API errors.
        - Add a token/length guard on `prompt` for very large contexts.
        - Consider streaming responses for a nicer chat UX.
    """
    response = _model.generate_content(prompt)
    return response.text
