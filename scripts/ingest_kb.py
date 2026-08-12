"""
Rebuild knowledge base from data/knowledge-base/ directory.
Usage: python scripts/ingest_kb.py
"""

import asyncio
from kb.loader import build_knowledge_base


async def main():
    print("🔄 Rebuilding knowledge base...")
    await build_knowledge_base()
    print("✅ Knowledge base indexed successfully")


if __name__ == "__main__":
    asyncio.run(main())
