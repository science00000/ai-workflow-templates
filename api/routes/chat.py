"""
Chat route — REST + WebSocket endpoints for live chat.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
import json

from agent.graph.support_graph import build_graph
from kb.loader import query_knowledge_base

router = APIRouter()
graph = build_graph()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    chat_history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    needs_escalation: bool
    sources: List[str] = []


@router.post("/")
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and get an AI response."""
    state = {
        "message": request.message,
        "intent": "",
        "kb_results": [],
        "response": "",
        "confidence": 0.0,
        "needs_escalation": False,
        "chat_history": request.chat_history,
    }

    result = await graph.ainvoke(state, {"configurable": {"thread_id": request.session_id}})

    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        confidence=result["confidence"],
        needs_escalation=result["needs_escalation"],
        sources=[r.get("source", "") for r in result.get("kb_results", [])],
    )


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """Real-time WebSocket chat endpoint."""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            request = ChatRequest(**json.loads(data))
            result = await chat(request)
            await websocket.send_text(json.dumps(result.model_dump()))
    except WebSocketDisconnect:
        pass
