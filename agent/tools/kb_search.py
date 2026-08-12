"""
Knowledge Base search tool for LangGraph agent.
"""

from kb.loader import query_knowledge_base


async def search_kb(query: str, top_k: int = 5) -> list[str]:
    """Search the knowledge base and return relevant text snippets."""
    results = await query_knowledge_base(query, top_k)
    return [r["content"] for r in results]
