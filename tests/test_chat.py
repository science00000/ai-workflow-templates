"""
Test chat endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(base_url="http://localhost:8000", timeout=10) as client:
        resp = await client.get("/health/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_chat():
    async with AsyncClient(base_url="http://localhost:8000", timeout=30) as client:
        resp = await client.post("/api/chat/", json={
            "message": "How long does shipping take?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "intent" in data
