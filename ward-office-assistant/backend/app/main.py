"""
Ward Office Assistant — FastAPI entrypoint.

Wires up:
    - CORS (so the React dev server can call the API)
    - API routers (chat, documents, services)
    - startup/shutdown hooks (DB connection, vector store warm-up, etc.)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import chat, documents, services

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-assisted Citizen Guidance Platform for ward offices.",
    version="0.1.0",
)

from app.db.base import Base
from app.db.session import engine
from app.models import user, service, office  # noqa: F401  (registers tables)

Base.metadata.create_all(bind=engine)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# TODO: add auth.py and admin.py routers once the admin panel + login flow
# are implemented (see docs/architecture.md).
app.include_router(chat.router, prefix="/api/chat", tags=["Chat / RAG Assistant"])
app.include_router(documents.router, prefix="/api/documents", tags=["Document Readiness"])
app.include_router(services.router, prefix="/api/services", tags=["Ward Services & Checklists"])


@app.get("/api/health", tags=["Health"])
def health_check():
    """Simple liveness probe used by Docker/uptime checks."""
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}


# TODO: on startup, consider:
#   - verifying the ChromaDB collection exists (create if missing)
#   - checking DB migrations are up to date
#   - warming up the BGE-M3 embedding model so the first request isn't slow
