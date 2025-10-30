from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ─────────────────────────────────────
    APP_NAME: str = "YouTube Multimodal RAG API"
    DEBUG: bool = False

    # ── MinIO ───────────────────────────────────
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "video-assets"
    MINIO_SECURE: bool = False

    # ── Qdrant ──────────────────────────────────
    QDRANT_URL: str = "http://qdrant:6333"

    # ── Redis ───────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ── Ollama (Llava) ──────────────────────────
    OLLAMA_MODEL: str = "llava:3b-q4_0"
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # ── Embedding Models ────────────────────────
    TEXT_EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    IMAGE_EMBED_MODEL: str = "ViT-B/32"
    EMBED_DEVICE: Literal["cpu", "cuda"] = "cpu"

    # ── Video Processing ────────────────────────
    FRAME_FPS: float = 0.2
    MAX_VIDEO_HEIGHT: int = 720

    # ── API ────────────────────────
    CHAT_APP_PORT: int = 8080

    model_config = {
        "env_file": ".env",  # ← Load from .env
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()
