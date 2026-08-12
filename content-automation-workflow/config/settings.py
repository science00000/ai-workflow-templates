"""
Content Automation Workflow — Pydantic Settings

Reads environment variables from .env and provides typed config
for the FastAPI application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Server ──────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # ── LLM Backend ─────────────────────────────────────────
    llm_backend: str = "ollama"            # ollama | openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com"

    # ── Content Defaults ────────────────────────────────────
    content_default_language: str = "en"
    content_tone: str = "professional"
    content_blog_min_words: int = 800
    content_blog_max_words: int = 2000
    content_social_count: int = 3
    content_email_format: str = "html"

    # ── Publishing ──────────────────────────────────────────
    wordpress_url: str = ""
    wordpress_user: str = ""
    wordpress_password: str = ""

    twitter_bearer_token: str = ""
    facebook_access_token: str = ""
    linkedin_access_token: str = ""

    mail_from: str = ""
    mail_host: str = ""
    mail_port: int = 587
    mail_user: str = ""
    mail_password: str = ""

    # ── n8n ─────────────────────────────────────────────────
    n8n_webhook_url: str = "http://localhost:5678/webhook/content"
    n8n_api_key: str = ""

    # ── Rate Limiting ───────────────────────────────────────
    rate_limit_requests: int = 30
    rate_limit_window: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
