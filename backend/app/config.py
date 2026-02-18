"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    port: int = 3001
    cors_origin: str = "http://localhost:5173"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # AI/ML endpoints (placeholder — replace with real endpoints)
    llm_endpoint: str = "http://localhost:11434/api/generate"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    image_classifier_endpoint: str = "http://localhost:8000/classify"
    stt_endpoint: str = "http://localhost:8001/transcribe"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
