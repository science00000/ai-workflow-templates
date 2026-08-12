"""
Health check routes
"""

from fastapi import APIRouter
from config.settings import settings

router = APIRouter()


@router.get("/")
async def health():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "Content Automation Workflow",
        "version": "1.0.0",
        "llm_backend": settings.llm_backend,
    }


@router.get("/llm")
async def llm_health():
    """Check if LLM backend is reachable."""
    from services.ollama_client import generate
    try:
        result = await generate("Say 'ok' in one word.", max_tokens=5)
        return {"status": "ok", "llm_backend": settings.llm_backend, "response": result.strip()}
    except Exception as e:
        return {"status": "error", "llm_backend": settings.llm_backend, "error": str(e)}
