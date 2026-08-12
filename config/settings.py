"""
Application settings loaded from .env / environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # LLM
    llm_backend: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "knowledge_base"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/support_bot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Knowledge Base
    kb_data_dir: str = "./data/knowledge-base"
    kb_rebuild_on_start: bool = True
    kb_top_k: int = 5

    # n8n
    n8n_webhook_url: str = ""
    n8n_api_key: str = ""

    # Chat
    wechat_secret: str = "change-me"
    allowed_origins: List[str] = ["*"]

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
