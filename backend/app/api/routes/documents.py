import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.ingestion import ingest_pdf, load_index
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and ingest a medical PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large. Max 50MB.")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = ingest_pdf(tmp_path)
        return {
            "message": f"Successfully ingested {file.filename}",
            "chunks_created": result["chunks_created"],
            "filename": file.filename
        }
    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        os.unlink(tmp_path)

@router.get("/status")
async def index_status():
    """Check if FAISS index is loaded."""
    from app.services.ingestion import get_index_state
    index, metadata, bm25 = get_index_state()
    return {
        "index_loaded": index is not None,
        "total_chunks": len(metadata),
        "bm25_ready": bm25 is not None,
        "sources": list(set(c["source"] for c in metadata)) if metadata else []
    }