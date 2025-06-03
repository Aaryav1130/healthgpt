from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["monitoring"])

# Metrics
QUERY_COUNTER = Counter("healthgpt_queries_total", "Total chat queries")
RETRIEVAL_LATENCY = Histogram(
    "healthgpt_retrieval_latency_seconds",
    "Retrieval + rerank latency",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
ACTIVE_USERS = Gauge("healthgpt_active_sessions", "Active SSE sessions")

@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)