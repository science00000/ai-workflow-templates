"""
AI Customer Support Bot — Application Entry Point

FastAPI server with LangGraph agent, Qdrant knowledge base,
and real-time WebSocket chat support.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ── Lifecycle ──────────────────────────────────────────────
from config.settings import settings
from db.session import init_db
from kb.loader import build_knowledge_base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: connect DB, build KB. Shutdown: cleanup."""
    await init_db()
    if settings.kb_rebuild_on_start:
        await build_knowledge_base()
    print(f"[bot] Listening on {settings.host}:{settings.port}")
    yield
    print("[bot] Shutting down")

# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="AI Customer Support Bot",
    description="Self-deployable AI customer support with RAG pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────
from api.routes.chat import router as chat_router
from api.routes.knowledge import router as kb_router
from api.routes.health import router as health_router
from api.routes.admin import router as admin_router

app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(kb_router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# ── Static / Web UI ────────────────────────────────────────
if os.path.isdir("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
