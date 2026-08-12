# AI Customer Support Bot Template

> Self-deployable AI customer support system with RAG pipeline, local LLM, and web chat UI.
> **Deploy in 15 minutes. No cloud account needed.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-blue)

---

## 📋 What You Get

| Component | Description |
|-----------|-------------|
| **FastAPI Backend** | REST + WebSocket chat API |
| **LangGraph Agent** | Multi-node conversation flow with intent classification |
| **Qdrant Vector DB** | Knowledge base with semantic search (RAG) |
| **Local LLM** | Ollama + Llama 3.2 (no API keys needed) |
| **Web Chat UI** | Ready-to-use customer-facing chat widget |
| **n8n Workflow** | Automation: webhook → classify → KB → respond → escalate |
| **Docker Compose** | One-command deploy with all dependencies |

---

## 🚀 Quick Start (3 commands)

```bash
git clone https://github.com/your-repo/ai-customer-support-bot.git
cd ai-customer-support-bot
bash deploy/quick-deploy.sh
```

That's it! Your bot will be running at **http://localhost:8000/chat** in ~10 minutes.

---

## 📁 Project Structure

```
ai-customer-support-bot-template/
├── main.py                        # FastAPI application entry
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment config template
├── .gitignore
│
├── config/
│   └── settings.py                # Pydantic settings from .env
│
├── agent/
│   ├── graph/
│   │   └── support_graph.py       # LangGraph agent pipeline
│   ├── prompts/
│   │   └── system.md              # System prompts
│   └── tools/
│       └── kb_search.py           # Knowledge base search tool
│
├── api/
│   └── routes/
│       ├── chat.py                # Chat REST + WebSocket
│       ├── knowledge.py           # KB management
│       ├── health.py              # Health checks
│       └── admin.py               # Admin/metrics
│
├── kb/
│   └── loader.py                  # KB ingestion into Qdrant
│
├── db/
│   └── session.py                 # Async PostgreSQL session
│
├── data/
│   └── knowledge-base/
│       └── faq.md                 # Sample FAQ (replace with yours)
│
├── n8n/
│   ├── workflows/
│   │   └── customer-support-bot.json  # n8n workflow definition
│   └── credentials/
│       └── README.md              # Credential setup guide
│
├── web/
│   ├── static/                    # CSS, JS assets
│   └── templates/
│       └── chat.html              # Web chat UI
│
├── deploy/
│   ├── docker/
│   │   ├── docker-compose.yml     # Full stack compose file
│   │   └── Dockerfile             # Multi-stage Docker build
│   ├── cloud/
│   │   ├── aws/                   # AWS deployment scripts
│   │   └── gcp/                   # GCP deployment scripts
│   └── quick-deploy.sh            # One-command deploy script
│
├── tests/
│   ├── test_chat.py               # Chat endpoint tests
│   ├── test_kb.py                 # KB search tests
│   └── test_graph.py              # Agent graph tests
│
├── scripts/
│   ├── ingest_kb.py               # Manual KB re-index script
│   └── eval_responses.py          # Evaluate bot response quality
│
├── docs/
│   └── api-reference.md           # API documentation
│
└── .github/
    └── workflows/
        └── deploy.yml             # CI pipeline
```

---

## 🛠️ Setup Guide

### Prerequisites
- **Docker & Docker Compose** (v24+)
- **4GB+ RAM** (8GB recommended for LLM)
- **Python 3.12+** (for local development)

### Step 1: Clone & Configure
```bash
git clone <your-repo-url>
cd ai-customer-support-bot-template
cp .env.example .env
# Edit .env — change POSTGRES_PASSWORD, OLLAMA_MODEL, etc.
```

### Step 2: Deploy
```bash
bash deploy/quick-deploy.sh
```

This starts 5 services:
- **app** — FastAPI on port 8000
- **qdrant** — Vector DB on port 6333
- **db** — PostgreSQL on port 5432
- **redis** — Cache on port 6379
- **ollama** — Local LLM on port 11434

### Step 3: Add Your Knowledge Base
Drop your documents into `data/knowledge-base/`:
```bash
cp your-faq.md data/knowledge-base/
curl -X POST http://localhost:8000/api/knowledge/rebuild
```

Supported formats: `.md`, `.txt`, `.json`

### Step 4: Customize the Bot
Edit `agent/prompts/system.md` to change the bot's personality, tone, and response rules.

### Step 5: Embed the Chat Widget
Add this to your website:
```html
<iframe src="http://localhost:8000/chat" width="480" height="600" style="border:none;border-radius:16px;"></iframe>
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/` | Send message, get AI response |
| `WS` | `/api/chat/ws` | WebSocket real-time chat |
| `GET` | `/api/knowledge/` | List KB entries |
| `POST` | `/api/knowledge/search` | Search knowledge base |
| `POST` | `/api/knowledge/rebuild` | Re-index all documents |
| `POST` | `/api/knowledge/upload` | Upload new document |
| `GET` | `/health/` | Health check |
| `GET` | `/admin/stats` | Conversation statistics |

Full API docs: **http://localhost:8000/docs** (Swagger UI)

---

## 🔄 n8n Workflow

Import `n8n/workflows/customer-support-bot.json` into your n8n instance.

**Workflow flow:**
```
Webhook → Classify Intent → Route by Intent
                                    ├─ KB Lookup → Generate → Confidence Check
                                    │                                      ├─ Response ✅
                                    │                                      └─ Escalate 🚨
                                    ├─ Direct Response (greetings)
                                    └─ Escalate to Human
```

See `n8n/credentials/README.md` for credential setup.

---

## 🧠 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Chat Widget  │────▶│  FastAPI     │────▶│  LangGraph   │
│  (Web/Mobile) │◀────│  Server      │◀────│  Agent       │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                     ┌──────▼───────┐     ┌───────▼──────┐
                     │   PostgreSQL │     │   Qdrant     │
                     │  (Sessions)  │     │  (Vector KB) │
                     └──────────────┘     └───────┬──────┘
                                                  │
                                    ┌─────────────▼────────┐
                                    │   Ollama (Llama 3.2) │
                                    │   Embeddings + Chat   │
                                    └───────────────────────┘
```

---

## 📊 Customization Guide

### Change LLM
Edit `.env`:
```
OLLAMA_MODEL=mistral      # or llama3, phi3, etc.
```
Or use cloud LLM:
```
LLM_BACKEND=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

### Change Embedding Model
```
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIM=768
```

### Add New Intent
1. Add intent to `agent/graph/support_graph.py` → `classify_intent()`
2. Add route in n8n workflow `Route by Intent` node
3. Add KB entries for the new intent

### Add Slack/Email Notifications
Configure n8n credentials and enable the `Notify Team (Slack)` node.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How long does shipping take?"}'

# Test KB search
curl -X POST http://localhost:8000/api/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "refund policy", "top_k": 3}'
```

---

## ☁️ Cloud Deployment

| Platform | Guide | Cost |
|----------|-------|------|
| AWS EC2 | `deploy/cloud/aws/README.md` | ~$15-30/mo |
| GCP Compute | `deploy/cloud/gcp/README.md` | ~$15-30/mo |
| Railway | `railway.json` config | Pay per usage |
| Render | `render.yaml` config | Free tier available |

---

## 🛑 Troubleshooting

| Problem | Solution |
|---------|----------|
| Ollama model fails to pull | Check internet connection; try smaller model (`llama3.2:1b`) |
| Port 8000 already in use | Change `PORT` in `.env` |
| Qdrant connection refused | Wait for Qdrant to start (`docker compose ps`) |
| Slow responses | Use a smaller model or increase RAM |
| KB not found | Run `curl -X POST http://localhost:8000/api/knowledge/rebuild` |

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

**Need help?** Open an issue or contact support@example.com
