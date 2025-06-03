from fastapi import APIRouter
import httpx
from app.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    # Check Ollama
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return {
        "status": "healthy" if ollama_ok else "degraded",
        "version": settings.app_version,
        "ollama": "up" if ollama_ok else "down",
        "model": settings.llm_model,
    }