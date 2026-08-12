"""
Test knowledge base operations.
"""

import pytest
from kb.loader import chunk_document


def test_chunk_document():
    doc = {
        "id": "test-1",
        "content": "A" * 1000,
        "file": "test.md",
    }
    chunks = chunk_document(doc, chunk_size=300, overlap=50)
    assert len(chunks) >= 3
    assert all("A" * 50 in c["content"] for c in chunks)
