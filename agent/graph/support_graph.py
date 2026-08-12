"""
LangGraph Agent Graph — Customer Support Conversation Flow

Nodes:
  classify → route → lookup_kb → generate → escalate? → respond
"""

import json
import logging
import re
from pathlib import Path
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from openai import OpenAI

from config.settings import settings
from kb.loader import load_documents, chunk_document

logger = logging.getLogger(__name__)

# ── LLM Client (OpenAI-compatible — works with Ollama or OpenAI) ──

def _get_client() -> OpenAI:
    """Build OpenAI client from settings. Supports Ollama via base_url."""
    if settings.llm_backend == "ollama":
        return OpenAI(
            api_key="ollama",
            base_url=f"{settings.ollama_base_url}/v1",
        )
    return OpenAI(
        api_key=settings.openai_api_key or "sk-placeholder",
        base_url=settings.openai_base_url,
    )


def _get_model() -> str:
    if settings.llm_backend == "ollama":
        return settings.ollama_model
    return settings.openai_model


# ── State ──────────────────────────────────────────────────
class AgentState(dict):
    """Conversation state passed between LangGraph nodes."""
    pass


# ── Prompts ────────────────────────────────────────────────

CLASSIFY_SYSTEM_PROMPT = """Bạn là agent phân loại intent cho bộ phận chăm sóc khách hàng.
Phân loại tin nhắn vào 1 trong các intents sau:

- "general_question" — Hỏi chung về sản phẩm, dịch vụ, tính năng
- "order_status" — Hỏi về đơn hàng, thanh toán, vận chuyển
- "refund" — Hỏi về hoàn tiền, hủy đơn
- "technical" — Hỏi về lỗi kỹ thuật, cài đặt, hướng dẫn sử dụng
- "greeting" — Chào hỏi, cảm ơn,Small talk
- "escalation" — Yêu cầu nhân viên, khiếu nại, không hài lòng

Trả lời CHỈ JSON, không thêm text khác:
{"intent": "<intent_name>", "confidence": <0.0-1.0>, "reasoning": "<ngắn gọn>"}
Luôn trả về JSON hợp lệ."""


RESPONSE_SYSTEM_PROMPT = """Bạn là trợ lý chăm sóc khách hàng thân thiện, chuyên nghiệp.

Yêu cầu:
- Trả lời dựa TRÊN THỰC TẾ từ thông tin KB bên dưới.
- Nếu không có thông tin trong KB, nói rõ bạn không biết và đề nghị chuyển cho nhân viên.
- Trả lời bằng cùng ngôn ngữ người dùng sử dụng.
- Ngắn gọn, hữu ích, tránh lan man.
- KHÔNG bịa thông tin.

Thông tin KB (nếu có):
{kb_context}

Lịch sử cuộc hội thoại:
{chat_history}"""


# ── Nodes ──────────────────────────────────────────────────

def classify_intent(state: AgentState) -> AgentState:
    """Classify user intent: general_question, order_status, refund, technical, greeting, escalation.

    Calls LLM with structured JSON prompt. Falls back to keyword-based
    classification when the LLM call fails or returns invalid JSON.
    """
    message = state.get("message", "")
    logger.info(f"[classify] Classifying: '{message[:80]}...'")

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.1,
            max_tokens=128,
        )
        content = resp.choices[0].message.content.strip()

        # Parse JSON — handle markdown fences and extra text
        intent, confidence, _ = _parse_json_response(content)

    except Exception as exc:
        logger.warning(f"[classify] LLM failed, falling back to keywords: {exc}")
        intent, confidence = _keyword_classify(message)

    state["intent"] = intent
    state["confidence"] = confidence
    logger.info(f"[classify] intent={intent}, confidence={confidence:.2f}")
    return state


def route_by_intent(state: AgentState) -> Literal["lookup_kb", "generate_direct", "escalate"]:
    """Route based on intent classification."""
    intent = state.get("intent", "")
    if intent in ("general_question", "order_status", "refund", "technical"):
        return "lookup_kb"
    elif intent in ("greeting", "thanks"):
        return "generate_direct"
    else:
        return "escalate"


def lookup_knowledge_base(state: AgentState) -> AgentState:
    """Search knowledge base for relevant entries.

    Strategy:
      1. Try vector search via Qdrant + sentence-transformers embeddings.
      2. Fall back to in-memory keyword search over raw KB files when
         Qdrant is unreachable or embeddings are unavailable.
    """
    message = state.get("message", "")
    intent = state.get("intent", "")
    top_k = settings.kb_top_k

    logger.info(f"[kb_lookup] Searching KB for intent='{intent}'")
    results = []

    # ── Attempt 1: Qdrant vector search ─────────────────────
    results = _vector_search(message, top_k)

    # ── Fallback: keyword search over raw KB files ──────────
    if not results:
        logger.info("[kb_lookup] Vector search returned nothing, using keyword fallback")
        results = _keyword_kb_search(message, intent, top_k)

    state["kb_results"] = results
    logger.info(f"[kb_lookup] Found {len(results)} KB results")
    return state


def generate_response(state: AgentState) -> AgentState:
    """Generate a response using LLM with RAG context and chat history.

    Builds a prompt from:
      - System prompt with KB context
      - Conversation history (last N turns)
      - Current user message
    """
    message = state.get("message", "")
    kb_results = state.get("kb_results", [])
    chat_history = state.get("chat_history", [])

    # Build KB context string
    kb_context = _format_kb_context(kb_results) if kb_results else "(không có thông tin KB phù hợp)"

    # Build chat history string (last 6 turns)
    history_text = _format_chat_history(chat_history[-6:])

    prompt = RESPONSE_SYSTEM_PROMPT.format(
        kb_context=kb_context,
        chat_history=history_text or "(không có lịch sử)",
    )

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
            max_tokens=512,
        )
        response_text = resp.choices[0].message.content.strip()

    except Exception as exc:
        logger.error(f"[generate] LLM failed: {exc}")
        # Graceful fallback
        if kb_results:
            response_text = kb_results[0].get("content", kb_results[0].get("answer", ""))
        else:
            response_text = (
                "Xin lỗi, tôi chưa tìm được thông tin phù hợp. "
                "Tôi sẽ chuyển câu hỏi của bạn cho nhân viên hỗ trợ."
            )

    state["response"] = response_text
    logger.info(f"[generate] Response: '{response_text[:80]}...'")
    return state


def check_escalation(state: AgentState) -> AgentState:
    """Decide if the response needs human escalation.

    Escalates when:
      - confidence < 0.5 (classification was uncertain)
      - intent is 'escalation' (user explicitly requested human)
      - no KB results found AND response contains uncertainty keywords
    """
    confidence = state.get("confidence", 0.0)
    intent = state.get("intent", "")
    kb_results = state.get("kb_results", [])
    response = state.get("response", "")

    needs_escalation = False
    reason = ""

    # Rule 1: explicit escalation intent
    if intent == "escalation":
        needs_escalation = True
        reason = "User requested human agent"

    # Rule 2: low confidence
    elif confidence < 0.5:
        needs_escalation = True
        reason = f"Low confidence ({confidence:.2f})"

    # Rule 3: no KB hits + uncertain response
    elif not kb_results:
        uncertain_phrases = [
            "không chắc", "không biết", "chưa có", "xin lỗi",
            "không tìm thấy", "không có thông tin", "không thể",
        ]
        if any(p in response.lower() for p in uncertain_phrases):
            needs_escalation = True
            reason = "No KB results and uncertain response"

    state["needs_escalation"] = needs_escalation
    if needs_escalation:
        state["response"] += (
            f"\n\n⚠️ {reason}. Câu hỏi của bạn đang được chuyển cho "
            "nhân viên hỗ trợ. Bạn sẽ nhận phản hồi trong 4 giờ."
        )
        logger.info(f"[escalation] Escalating: {reason}")
    else:
        logger.info("[escalation] No escalation needed")

    return state


# ── Build Graph ────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify", classify_intent)
    graph.add_node("lookup_kb", lookup_knowledge_base)
    graph.add_node("generate", generate_response)
    graph.add_node("check_escalation", check_escalation)

    # Entry point
    graph.set_entry_point("classify")

    # Conditional routing
    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "lookup_kb": "lookup_kb",
            "generate_direct": "generate",
            "escalate": "check_escalation",
        },
    )

    graph.add_edge("lookup_kb", "generate")
    graph.add_edge("generate", "check_escalation")
    graph.add_edge("check_escalation", END)

    # Compile with memory
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# ── Helpers ────────────────────────────────────────────────

def _parse_json_response(text: str) -> tuple[str, float, str]:
    """Extract JSON from LLM response, handling markdown fences."""
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try extracting JSON object from surrounding text
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start:end + 1])
        else:
            raise ValueError(f"Cannot parse JSON from: {text[:120]}")

    return (
        data.get("intent", "general_question"),
        float(data.get("confidence", 0.5)),
        data.get("reasoning", ""),
    )


def _keyword_classify(message: str) -> tuple[str, float]:
    """Fallback: keyword-based intent classification."""
    msg = message.lower()

    intent_keywords = {
        "order_status": ["đơn hàng", "order", "vận chuyển", "ship", "giao hàng",
                          "theo dõi", "tracking", "nơi nào", "đến chưa", "thanh toán",
                          "payment", "đặt hàng"],
        "refund": ["hoàn tiền", "refund", "hủy đơn", "cancel", "trả lại",
                    "hoàn trả", "money back"],
        "technical": ["lỗi", "error", "không hoạt động", "crash", "không mở",
                       "cài đặt", "setup", "không vào được", "bug", "sự cố",
                       "chậm", "hướng dẫn", "cách", "làm thế nào", "tutorial"],
        "greeting": ["xin chào", "chào", "hello", "hi", "thank", "cảm ơn",
                      "thanks", "cảm ơn bạn", "thanks a lot"],
        "escalation": ["nhân viên", "human", "quản lý", "trưởng nhóm", "khiếu nại",
                        "complain", "gọi cho", "số điện thoại", "không hài lòng",
                        "phàn nàn", "bad service"],
    }

    best_intent = "general_question"
    best_score = 0

    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in msg)
        if score > best_score:
            best_score = score
            best_intent = intent

    confidence = min(0.5 + best_score * 0.15, 0.9) if best_score > 0 else 0.3
    return best_intent, confidence


# ── KB Search ──────────────────────────────────────────────

def _vector_search(query: str, top_k: int) -> list[dict]:
    """Search KB via Qdrant + sentence-transformers embeddings."""
    try:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer

        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        embedder = SentenceTransformer(settings.embedding_model)
        vector = embedder.encode(query).tolist()

        hits = client.search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            limit=top_k,
        )

        return [
            {
                "content": hit.payload.get("content", ""),
                "score": round(hit.score, 4),
                "source": hit.payload.get("file", ""),
            }
            for hit in hits
            if hit.score > 0.3  # Minimum relevance threshold
        ]

    except Exception as exc:
        logger.debug(f"[kb] Vector search unavailable: {exc}")
        return []


def _keyword_kb_search(query: str, intent: str, top_k: int) -> list[dict]:
    """In-memory keyword search over raw KB files when vector search fails."""
    kb_dir = settings.kb_data_dir
    if not kb_dir or not Path(kb_dir).exists():
        logger.warning(f"[kb] KB directory not found: {kb_dir}")
        return []

    # Load and chunk all docs
    docs = load_documents(kb_dir)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    if not all_chunks:
        return []

    # Tokenise query
    stop_words = {
        "và", "không", "được", "có", "cái", "nào", "làm", "thế", "nào",
        "là", "cho", "về", "với", "tại", "sao", "the", "a", "an", "is",
        "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may",
        "might", "of", "to", "in", "for", "on", "with", "at", "by",
        "from", "as", "into", "through", "during", "before", "after",
        "above", "below", "between", "and", "but", "or", "nor", "not",
        "so", "yet", "both", "either", "neither", "each", "every",
        "all", "any", "few", "more", "most", "other", "some", "such",
        "no", "only", "own", "same", "than", "too", "very", "can",
    }
    query_words = set(
        w for w in query.lower().split()
        if len(w) > 2 and w not in stop_words
    )

    # Score each chunk
    scored = []
    for chunk in all_chunks:
        text = chunk["content"].lower()

        score = 0
        if query_words:
            score = sum(1 for w in query_words if w in text)

        # Bonus for intent-aligned chunks
        intent_hints = {
            "order_status": ["đơn", "giao", "ship", "vận chuyển", "track", "order"],
            "refund": ["hoàn", "hủy", "cancel", "refund", "trả"],
            "technical": ["lỗi", "error", "bug", "cài đặt", "setup", "không hoạt động"],
        }
        for hint in intent_hints.get(intent, []):
            if hint in text:
                score += 1.5

        if score > 0:
            scored.append((score, chunk))

    # Sort descending, take top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    # Normalise scores to [0, 1]
    if top:
        max_score = top[0][0]
        return [
            {
                "content": chunk["content"],
                "score": round(s / max(max_score, 1), 4),
                "source": chunk.get("source", chunk.get("metadata", {}).get("file", "")),
            }
            for s, chunk in top
        ]

    return []


# ── Formatting ─────────────────────────────────────────────

def _format_kb_context(results: list[dict]) -> str:
    """Format KB results into a readable context block for the LLM prompt."""
    parts = []
    for i, r in enumerate(results, 1):
        content = r.get("content", r.get("answer", ""))
        parts.append(f"[KB-{i}] {content}")
    return "\n\n".join(parts)


def _format_chat_history(history: list) -> str:
    """Format chat history into a readable string for the LLM prompt."""
    if not history:
        return ""
    lines = []
    for turn in history:
        role = turn.get("role", "user").capitalize()
        text = turn.get("content", "")
        lines.append(f"{role}: {text}")
    return "\n".join(lines)
