"""
Health check endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health():
    return {"status": "ok", "service": "ai-customer-support-bot"}


@router.get("/ready")
async def readiness():
    # TODO: Check DB, Qdrant, LLM connectivity
    return {"status": "ready"}
