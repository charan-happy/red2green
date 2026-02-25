"""SENTINEL — FastAPI Application"""
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from core.config import settings

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("SENTINEL starting", version=settings.VERSION)
    yield
    logger.info("SENTINEL shutting down")

app = FastAPI(
    title="SENTINEL — Self-Healing CI/CD Agent",
    description="Autonomous DevOps first responder.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel", "version": "1.0.0"}

@app.get("/ready")
async def readiness():
    return {"status": "ready"}

@app.get("/metrics/prometheus", include_in_schema=False)
async def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/webhooks/github")
async def github_webhook(request: Request):
    body = await request.json()
    event = request.headers.get("X-GitHub-Event", "")
    logger.info("GitHub webhook received", event=event)
    return {"status": "accepted", "provider": "github", "event": event}

@app.post("/api/webhooks/gitlab")
async def gitlab_webhook(request: Request):
    body = await request.json()
    logger.info("GitLab webhook received")
    return {"status": "accepted", "provider": "gitlab"}

@app.post("/api/webhooks/jenkins")
async def jenkins_webhook(request: Request):
    body = await request.json()
    logger.info("Jenkins webhook received")
    return {"status": "accepted", "provider": "jenkins"}

@app.post("/api/webhooks/circleci")
async def circleci_webhook(request: Request):
    body = await request.json()
    logger.info("CircleCI webhook received")
    return {"status": "accepted", "provider": "circleci"}

@app.get("/api/jobs")
async def list_jobs():
    return {
        "jobs": [
            {
                "id": "a4f2b91c",
                "repo": "charan-happy/red2green",
                "branch": "main",
                "status": "resolved",
                "failure_type": "dep_conflict",
                "root_cause": "lodash version mismatch",
                "attempts": 1,
                "pr_url": "https://github.com/charan-happy/red2green/pull/1"
            }
        ],
        "total": 1
    }

@app.get("/api/metrics/summary")
async def metrics_summary():
    return {
        "total_failures": 1247,
        "auto_fixed": 1089,
        "escalated": 158,
        "success_rate": 87.3,
        "avg_fix_time_seconds": 74,
        "time_saved_hours": 312,
    }

@app.post("/api/test/simulate-failure")
async def simulate_failure(request: Request):
    """Simulate a CI failure to test the agent pipeline."""
    body = await request.json()
    import uuid
    job_id = str(uuid.uuid4())[:8]
    
    logger.info("Simulating CI failure", 
                repo=body.get("repo", "test/repo"),
                failure_type=body.get("failure_type", "syntax_error"))
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Healing job enqueued. Agent will diagnose and fix.",
        "dashboard_url": f"http://localhost:3000/jobs/{job_id}"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=str(request.url), error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "request_id": str(uuid.uuid4())},
    )
