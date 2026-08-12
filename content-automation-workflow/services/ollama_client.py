"""
Ollama LLM client service

Wraps Ollama (or OpenAI-compatible) API for content generation.
Supports streaming and structured JSON output.
"""

import json
import httpx
from typing import Optional
from config.settings import settings

_client: Optional[httpx.AsyncClient] = None


async def init_ollama():
    """Create the HTTP client for LLM calls."""
    global _client
    _client = httpx.AsyncClient(timeout=120.0)


async def generate(prompt: str, system: str = "", max_tokens: int = 4096) -> str:
    """
    Generate text using the configured LLM backend.

    Args:
        prompt: User prompt
        system: System prompt (role context)
        max_tokens: Maximum output tokens

    Returns:
        Generated text
    """
    if settings.llm_backend == "ollama":
        return await _ollama_generate(prompt, system, max_tokens)
    else:
        return await _openai_generate(prompt, system, max_tokens)


async def _ollama_generate(prompt: str, system: str, max_tokens: int) -> str:
    """Call Ollama /api/generate."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await _client.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        },
    )
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "")


async def _openai_generate(prompt: str, system: str, max_tokens: int) -> str:
    """Call OpenAI-compatible API."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await _client.post(
        f"{settings.openai_base_url}/v1/chat/completions",
        json={
            "model": settings.openai_model,
            "messages": messages,
            "max_tokens": max_tokens,
        },
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def generate_json(prompt: str, system: str = "") -> dict:
    """
    Generate structured JSON output.

    Returns:
        Parsed JSON dict
    """
    text = await generate(prompt, system + "\n\nRespond ONLY with valid JSON.")
    # Strip markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)
