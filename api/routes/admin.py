"""
Admin routes — metrics, stats, manual triggers.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/stats")
async def get_stats():
    """Get conversation statistics from Redis/PostgreSQL."""
    return {
        "total_conversations": 0,
        "avg_response_time_ms": 0,
        "escalation_rate": 0.0,
        "top_intents": {},
    }


@router.post("/clear-cache")
async def clear_cache():
    """Clear conversation cache from Redis."""
    return {"status": "ok"}
