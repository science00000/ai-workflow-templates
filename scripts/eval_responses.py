"""
Evaluate bot responses against golden Q&A pairs.
Usage: python scripts/eval_responses.py
"""

import httpx
import json


GOLDEN_QA = [
    {
        "question": "How long does shipping take?",
        "expected_keywords": ["5-7", "business days"],
    },
    {
        "question": "What is your return policy?",
        "expected_keywords": ["30-day", "return"],
    },
    {
        "question": "How do I reset my password?",
        "expected_keywords": ["forgot password", "reset link"],
    },
]


async def evaluate():
    passed = 0
    failed = 0

    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30) as client:
        for qa in GOLDEN_QA:
            resp = await client.post("/api/chat/", json={"message": qa["question"]})
            data = resp.json()
            answer = data.get("response", "").lower()

            hit = all(kw.lower() in answer for kw in qa["expected_keywords"])
            if hit:
                passed += 1
                print(f"✅ PASS: {qa['question']}")
            else:
                failed += 1
                print(f"❌ FAIL: {qa['question']}")
                print(f"   Response: {answer[:200]}")

    total = passed + failed
    print(f"\n📊 Results: {passed}/{total} passed ({100*passed//total}% accuracy)")
    return passed, total


if __name__ == "__main__":
    import asyncio
    asyncio.run(evaluate())
