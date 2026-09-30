"""
Centralized application configuration, loaded from environment variables
(see .env.example at the repo root). Every other module should import
`settings` from here rather than reading os.environ directly.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Ward Office Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg2://ward_admin:changeme@localhost:5432/ward_office_assistant"

    # --- Auth ---
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- LLM (Gemini) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Embeddings ---
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"

    # --- Vector DB (Chroma) ---
    CHROMA_PERSIST_DIR: str = "./data/indexes"
    CHROMA_COLLECTION_NAME: str = "ward_knowledge_base"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # --- OCR ---
    OCR_LANG: str = "en"
    OCR_USE_GPU: bool = False

    # --- Uploads ---
    MAX_UPLOAD_SIZE_MB: int = 10
    TMP_UPLOAD_DIR: str = "./backend/tmp_uploads"

    model_config = SettingsConfigDict(
    env_file=Path(__file__).resolve().parents[3] / ".env",  # repo-root .env
    extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
