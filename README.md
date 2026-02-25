# PatchPilot — Autonomous Self-Healing CI/CD Agent

> AGE OF AGENTS Hackathon | Track: Self-Testing Code Responder (SDLC)

PatchPilot autonomously watches CI/CD pipelines and heals broken builds — before a human needs to wake up.

## 🚀 Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your keys (already configured if you ran setup.sh)

# 2. Start the stack
docker-compose up -d

# 3. Test the agent
python scripts/test_agent.py

# 4. View API docs
open http://localhost:8000/api/docs
```

## 🧠 How It Works

```
CI Failure Detected
      │
      ▼
[INGEST] Fetch repo files at failing commit
      │
      ▼
[DIAGNOSE] Claude analyzes error log → failure_type, root_cause, confidence
      │
      ├─ low confidence → [ESCALATE] → Slack/PagerDuty/Email
      │
      ▼
[RETRIEVE] pgvector RAG search for similar past fixes
      │
      ▼
[GENERATE FIX] Claude generates surgical code patches
      │
      ▼
[VALIDATE] Run patches in isolated Docker sandbox
      │
      ├─ pass → [OPEN PR] with full diagnostic context
      │
      └─ fail (retry with higher temperature) → [ESCALATE] after max attempts
```

## 🔌 CI Provider Support

| Provider | Webhook Endpoint |
|---------|-----------------|
| GitHub Actions | `POST /api/webhooks/github` |
| GitLab CI | `POST /api/webhooks/gitlab` |
| Jenkins | `POST /api/webhooks/jenkins` |
| CircleCI | `POST /api/webhooks/circleci` |

## 📚 Tech Stack

- **Agent:** LangGraph state machine
- **LLM:** Claude claude-sonnet-4-6 (Anthropic)
- **Database:** PostgreSQL 16 + pgvector (semantic fix memory)
- **Queue:** Redis Streams
- **Sandbox:** Docker (isolated, network-free)
- **Backend:** FastAPI + Python async
- **Observability:** Prometheus + Grafana

## 🌐 Endpoints

| Endpoint | Description |
|---------|-------------|
| `GET /health` | Health check |
| `GET /api/docs` | Interactive API docs |
| `GET /api/jobs` | List healing jobs |
| `GET /api/metrics/summary` | Platform metrics |
| `POST /api/test/simulate-failure` | Test the agent |

## ⚙️ Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...      # Required
GITHUB_TOKEN=ghp_...              # For PR creation
GITHUB_WEBHOOK_SECRET=...         # Webhook verification
SLACK_BOT_TOKEN=xoxb-...         # Optional notifications
PAGERDUTY_ROUTING_KEY=...         # Optional escalation
```

## 🚀 Production Deployment

```bash
# Using Docker Compose
docker-compose -f docker-compose.yml up -d

# Scale workers by updating docker-compose.yml and redeploying
docker-compose up -d --scale worker=8
```

---

*Built for the AGE OF AGENTS Hackathon — PatchPilot turns red builds green, automatically.*
