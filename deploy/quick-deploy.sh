# AI Customer Support Bot — Quick Deploy Script
# Usage: bash deploy/quick-deploy.sh

set -euo pipefail

echo "╔══════════════════════════════════════════╗"
echo "║  AI Customer Support Bot — Quick Deploy  ║"
echo "║  Estimated time: 10-15 minutes           ║"
echo "╚══════════════════════════════════════════╝"

# ── Prerequisites check ───────────────────────────────────
check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        echo "❌ Missing: $1"
        MISSING+=("$1")
    fi
}

MISSING=()
check_cmd docker
check_cmd docker compose || check_cmd docker-compose
check_cmd curl

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "Required tools not found: ${MISSING[*]}"
    echo "Install Docker Desktop: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Prerequisites OK"

# ── Copy .env ──────────────────────────────────────────────
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "   → Edit .env if you need custom settings"
fi

# ── Pull Ollama model ──────────────────────────────────────
echo "🧠 Pulling Ollama model (llama3.2)..."
docker run --rm ollama/ollama ollama pull llama3.2 2>/dev/null || true

# ── Start services ─────────────────────────────────────────
echo "🚀 Starting services..."
cd deploy/docker
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."

# ── Wait for health ────────────────────────────────────────
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health/ >/dev/null 2>&1; then
        echo ""
        echo "✅ All services are up!"
        echo ""
        echo "📊 Services running:"
        docker compose ps
        echo ""
        echo "🌐 Chat API:    http://localhost:8000/api/chat/"
        echo "📚 Knowledge:   http://localhost:8000/api/knowledge/"
        echo "📖 Docs:        http://localhost:8000/docs"
        echo "💬 Web Chat:    http://localhost:8000/chat"
        echo ""
        echo "🛑 To stop:  cd deploy/docker && docker compose down"
        echo "📝 To tail:  cd deploy/docker && docker compose logs -f app"
        exit 0
    fi
    sleep 2
done

echo "⚠️  Services started but health check timed out."
echo "   Check logs: cd deploy/docker && docker compose logs"
