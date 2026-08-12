# Content Automation Workflow Template

> One topic → Blog post + Social media + Email newsletter — fully automated with local AI.
> **Deploy in 10 minutes. No API keys needed.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![n8n](https://img.shields.io/badge/n8n-workflow-orange)

---

## 📋 What You Get

| Component | Description |
|-----------|-------------|
| **FastAPI Backend** | REST API for content generation (blog, social, email) |
| **n8n Workflow** | Full automation: webhook → generate → publish |
| **Ollama LLM** | Local AI — no API costs, no cloud dependency |
| **Web UI** | Visual content generator dashboard |
| **Docker Compose** | One-command deploy with all services |
| **Content Templates** | Blog, social media, email templates with best practices |

---

## 🚀 Quick Start (3 commands)

```bash
cd content-automation-workflow
cp .env.example .env
docker compose -f deploy/docker/docker-compose.yml up -d
```

Your content API will be running at **http://localhost:8000** in ~5 minutes.

---

## 📁 Project Structure

```
content-automation-workflow/
├── main.py                                # FastAPI application entry
├── requirements.txt                       # Python dependencies
├── .env.example                           # Environment config template
├── .gitignore
│
├── config/
│   └── settings.py                        # Pydantic settings from .env
│
├── api/
│   └── routes/
│       ├── content.py                     # Content generation API
│       └── health.py                      # Health checks
│
├── services/
│   ├── ollama_client.py                   # Ollama/OpenAI LLM client
│   ├── content_generator.py               # Blog, social, email generation
│   └── publisher.py                       # WordPress, Twitter, Email publish
│
├── templates/
│   ├── blog/
│   │   └── blog-post-template.md          # Blog post structure guide
│   ├── social/
│   │   └── social-media-template.json     # Platform-specific templates
│   └── email/
│       └── email-newsletter-template.json # Email template + best practices
│
├── data/
│   └── samples/
│       └── topics.json                    # Sample content topics
│
├── n8n/
│   ├── workflows/
│   │   └── content-automation.json        # n8n workflow definition
│   └── credentials/
│       └── README.md                      # Credential setup guide
│
├── web/
│   └── templates/
│       └── generator.html                 # Content generator dashboard UI
│
├── deploy/
│   ├── docker/
│   │   ├── docker-compose.yml             # Full stack compose file
│   │   └── Dockerfile                     # Multi-stage Docker build
│
├── tests/
│   ├── test_content.py                    # Content generation tests
│   └── test_api.py                        # API endpoint tests
│
└── README.md                              # This file
```

---

## 🛠️ Setup Guide

### Prerequisites
- **Docker & Docker Compose** (v24+)
- **4GB+ RAM** (8GB recommended for LLM)
- **Python 3.12+** (for local development)

### Step 1: Clone & Configure
```bash
cp .env.example .env
# Edit .env — choose your model, set publishing credentials
```

### Step 2: Deploy with Docker
```bash
docker compose -f deploy/docker/docker-compose.yml up -d
```

This starts 3 services:
- **app** — FastAPI on port 8000
- **ollama** — Local LLM on port 11434
- **n8n** — Workflow automation on port 5678

### Step 3: Import n8n Workflow
1. Open **http://localhost:5678**
2. Go to Workflows → Import
3. Upload `n8n/workflows/content-automation.json`
4. Configure credentials (see `n8n/credentials/README.md`)
5. Activate the workflow

### Step 4: Generate Content
```bash
# Generate all content from one topic
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in content marketing", "tone": "professional"}'

# Generate blog post only
curl -X POST http://localhost:8000/api/content/blog \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in content marketing"}'

# Generate and save to disk
curl -X POST http://localhost:8000/api/content/save \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in content marketing", "tone": "casual"}'
```

### Step 5: Use the Web UI
Open **http://localhost:8000** in your browser for a visual content generator.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/generate` | Generate ALL content (blog + social + email) |
| `POST` | `/api/content/blog` | Generate blog post only |
| `POST` | `/api/content/social` | Generate social media posts |
| `POST` | `/api/content/email` | Generate email newsletter |
| `POST` | `/api/content/publish/blog` | Generate + publish to WordPress |
| `POST` | `/api/content/publish/email` | Generate + send via SMTP |
| `POST` | `/api/content/save` | Generate + save to disk |
| `GET` | `/health/` | Health check |
| `GET` | `/health/llm` | LLM connectivity check |

Full API docs: **http://localhost:8000/docs** (Swagger UI)

---

## 🔄 n8n Workflow

**Workflow flow:**
```
Content Request (Webhook/Cron)
           │
    ┌──────┼────────┐
    ▼      ▼        ▼
  Blog   Social   Email    ← Parallel generation via FastAPI
    │      │        │
    └──────┼────────┘
           ▼
    Merge All Content
           │
    ┌──────┼──────────────────┐
    ▼      ▼        ▼         ▼
  File   WordPress  Social   Email   ← Parallel publishing
    │      │        │         │
    └──────┼────────┼─────────┘
           ▼
    Slack Notification → Return Response
```

See `n8n/credentials/README.md` for credential setup.

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   n8n Workflow                       │
│  Webhook → [Blog] [Social] [Email] → Merge → Publish │
└──────────────────────────┬──────────────────────────┘
                           │ HTTP API
┌──────────────────────────▼──────────────────────────┐
│                  FastAPI Server                       │
│  /api/content/generate  (blog + social + email)      │
│  /api/content/blog          (blog only)               │
│  /api/content/social        (social only)             │
│  /api/content/email         (email only)              │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│                  Ollama (Local LLM)                  │
│  llama3.2 / mistral / phi3                          │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Customization Guide

### Change LLM
Edit `.env`:
```env
OLLAMA_MODEL=mistral      # or llama3, phi3, gemma2
```

### Change Content Defaults
```env
CONTENT_BLOG_MIN_WORDS=600
CONTENT_BLOG_MAX_WORDS=1500
CONTENT_SOCIAL_COUNT=5
CONTENT_DEFAULT_LANGUAGE=vi
```

### Add Publishing Targets
Configure in `.env`:
```env
WORDPRESS_URL=https://your-site.wordpress.com
WORDPRESS_USER=admin
WORDPRESS_PASSWORD=app_password_here
TWITTER_BEARER_TOKEN=xxx
FACEBOOK_ACCESS_TOKEN=xxx
```

### Customize Content Templates
Edit files in `templates/`:
- `templates/blog/blog-post-template.md` — Blog structure
- `templates/social/social-media-template.json` — Social post styles
- `templates/email/email-newsletter-template.json` — Email layout

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test content generation
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "10 Tips for Better Content Marketing"}'

# Test single endpoint
curl -X POST http://localhost:8000/api/content/blog \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in marketing", "tone": "casual"}'
```

---

## ☁️ Cloud Deployment

| Platform | Guide | Cost |
|----------|-------|------|
| AWS EC2 | `deploy/cloud/aws/README.md` | ~$15-30/mo |
| GCP Compute | `deploy/cloud/gcp/README.md` | ~$15-30/mo |
| Railway | Deploy via `docker-compose.yml` | Pay per usage |
| Render | `render.yaml` config | Free tier available |

---

## 🛑 Troubleshooting

| Problem | Solution |
|---------|----------|
| Ollama model fails to pull | Check internet; try smaller model (`llama3.2:1b`) |
| Port 8000 already in use | Change `PORT` in `.env` |
| Slow responses | Use a smaller model or increase RAM |
| JSON parse error in social/email | LLM returned non-JSON; increase model size |
| n8n can't reach API | Set `CONTENT_API_URL=http://app:8000` in n8n env |

---

## 📄 License

MIT License

---

**Need help?** Open an issue or contact support@example.com
