"""
Content Automation Workflow — Application Entry Point

FastAPI server with content generation API: blog posts, social media,
email newsletters — all from a single prompt input using local LLM.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from config.settings import settings
from services.ollama_client import init_ollama


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init LLM client. Shutdown: cleanup."""
    await init_ollama()
    print(f"[content] Content Automation API on {settings.host}:{settings.port}")
    yield
    print("[content] Shutting down")


# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="Content Automation Workflow",
    description="Generate blog posts, social media & email newsletters from 1 prompt",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────
from api.routes.content import router as content_router
from api.routes.health import router as health_router

app.include_router(content_router, prefix="/api/content", tags=["Content"])
app.include_router(health_router, prefix="/health", tags=["Health"])

# ── Static / Web UI ────────────────────────────────────────
if os.path.isdir("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the content generator UI."""
    if os.path.isfile("web/templates/generator.html"):
        with open("web/templates/generator.html") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Content Automation API</h1><p>Visit /docs for API.</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
