from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.services.ingestion import load_index
from app.api.routes import chat, documents, health
from app.monitoring.metrics import router as metrics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging(settings.debug)
    logger.info("Starting HealthGPT", version=settings.app_version)

    # Load pre-built FAISS index if it exists
    loaded = load_index()
    if loaded:
        logger.info("FAISS index loaded from disk")
    else:
        logger.info("No FAISS index found - please upload PDFs to /documents/upload")

    yield  # App running

    logger.info("Shutting down HealthGPT")

app = FastAPI(
    title="HealthGPT API",
    version=settings.app_version,
    description="Medical RAG API powered by LangGraph + FAISS + Llama 3",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS (allow React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(chat.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(metrics_router)