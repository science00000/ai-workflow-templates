# REST API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### Chat

#### POST /api/chat/
Send a message and receive an AI response.

**Request:**
```json
{
  "message": "How long does shipping take?",
  "session_id": "user-123",
  "chat_history": []
}
```

**Response:**
```json
{
  "response": "Standard shipping takes 5-7 business days...",
  "intent": "general_question",
  "confidence": 0.92,
  "needs_escalation": false,
  "sources": ["faq.md"]
}
```

#### WebSocket /api/chat/ws
Real-time chat connection.

**Send:**
```json
{"message": "Your question", "session_id": "user-123"}
```

**Receive:**
```json
{
  "response": "AI answer",
  "intent": "intent_type",
  "confidence": 0.95,
  "needs_escalation": false,
  "sources": []
}
```

### Knowledge Base

#### GET /api/knowledge/
List all knowledge base entries.

#### POST /api/knowledge/search
Search the knowledge base.

```json
{
  "query": "shipping policy",
  "top_k": 5
}
```

#### POST /api/knowledge/rebuild
Re-index all documents.

#### POST /api/knowledge/upload
Upload a new document (multipart/form-data).

### Health

#### GET /health/
```json
{"status": "ok", "service": "ai-customer-support-bot"}
```

#### GET /health/ready
Check if all dependencies are ready.

### Admin

#### GET /admin/stats
Get conversation statistics.

#### POST /admin/clear-cache
Clear conversation cache.

---

## Swagger UI
Interactive API docs available at: **http://localhost:8000/docs**
