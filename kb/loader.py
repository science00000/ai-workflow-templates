"""
Knowledge Base Loader — Ingest docs into Qdrant vector store.
"""

import os
import hashlib
from pathlib import Path
from qdrant_client import QdrantClient, models
from config.settings import settings


def load_documents(kb_dir: str = None) -> list[dict]:
    """Load all .md, .txt, .json files from knowledge base directory."""
    kb_dir = kb_dir or settings.kb_data_dir
    docs = []
    for filepath in Path(kb_dir).rglob("*"):
        if filepath.suffix in (".md", ".txt", ".json"):
            text = filepath.read_text(encoding="utf-8")
            docs.append({
                "file": str(filepath.relative_to(kb_dir)),
                "content": text,
                "id": hashlib.sha256(text.encode()).hexdigest()[:16],
            })
    return docs


def chunk_document(doc: dict, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Split a document into overlapping chunks for embedding."""
    content = doc["content"]
    chunks = []
    for i in range(0, len(content), chunk_size - overlap):
        chunk_text = content[i:i + chunk_size]
        if chunk_text.strip():
            chunks.append({
                "id": f"{doc['id']}-{i // (chunk_size - overlap)}",
                "content": chunk_text,
                "source": doc["file"],
                "metadata": {"file": doc["file"], "parent_id": doc["id"]},
            })
    return chunks


async def build_knowledge_base():
    """Ingest all KB documents into Qdrant."""
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    # Create collection if not exists
    try:
        client.get_collection(settings.qdrant_collection)
    except Exception:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.embedding_dim,
                distance=models.Distance.COSINE,
            ),
        )

    # Load & embed documents
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer(settings.embedding_model)

    docs = load_documents()
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    for chunk in all_chunks:
        vector = embedder.encode(chunk["content"]).tolist()
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                models.PointStruct(
                    id=hash(chunk["id"]) % (2**63),
                    vector=vector,
                    payload=chunk["metadata"] | {"content": chunk["content"]},
                )
            ],
        )

    print(f"[kb] Indexed {len(all_chunks)} chunks from {len(docs)} files")


async def query_knowledge_base(query: str, top_k: int = None) -> list[dict]:
    """Search knowledge base for relevant chunks."""
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    embedder = SentenceTransformer(settings.embedding_model)
    vector = embedder.encode(query).tolist()

    top_k = top_k or settings.kb_top_k
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=top_k,
    )

    return [
        {"content": hit.payload["content"], "score": hit.score, "source": hit.payload.get("file", "")}
        for hit in results
    ]
