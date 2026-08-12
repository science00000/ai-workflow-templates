"""
Knowledge Base management routes — add, list, delete entries.
"""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from kb.loader import build_knowledge_base, query_knowledge_base

router = APIRouter()


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.get("/")
async def list_entries():
    """List all knowledge base entries (from Qdrant scroll)."""
    # TODO: Implement scroll listing
    return {"entries": [], "total": 0}


@router.post("/search")
async def search_knowledge_base(req: KBSearchRequest):
    """Search knowledge base for relevant content."""
    results = await query_knowledge_base(req.query, req.top_k)
    return {"results": results}


@router.post("/rebuild")
async def rebuild_knowledge_base():
    """Re-index all knowledge base documents."""
    await build_knowledge_base()
    return {"status": "ok", "message": "Knowledge base rebuilt"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the knowledge base."""
    content = await file.read()
    import os
    from config.settings import settings
    path = os.path.join(settings.kb_data_dir, file.filename)
    with open(path, "wb") as f:
        f.write(content)
    await build_knowledge_base()
    return {"status": "ok", "file": file.filename}
