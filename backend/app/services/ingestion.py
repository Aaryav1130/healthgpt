import faiss
import numpy as np
import json
import os
import pickle
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from app.core.config import settings
from app.core.logging import logger
from app.utils.pdf_loader import extract_text_from_pdf
from app.utils.chunker import chunk_documents

_faiss_index: faiss.IndexFlatIP = None
_metadata: List[Dict] = []
_bm25_index: BM25Okapi = None
_embedding_model: SentenceTransformer = None

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model", model=settings.embedding_model)
        _embedding_model = SentenceTransformer(
            settings.embedding_model,
            device=settings.embedding_device
        )
    return _embedding_model

def embed_texts(texts: List[str]) -> np.ndarray:
    """Local embeddings — simple and reliable."""
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.astype(np.float32)

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def save_index(index: faiss.IndexFlatIP, metadata: List[Dict], bm25: BM25Okapi):
    os.makedirs(Path(settings.faiss_index_path).parent, exist_ok=True)
    faiss.write_index(index, settings.faiss_index_path)
    with open(settings.faiss_metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    with open(settings.faiss_index_path + "_bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)
    logger.info("Index saved", chunks=len(metadata))

def load_index():
    global _faiss_index, _metadata, _bm25_index
    if os.path.exists(settings.faiss_index_path):
        _faiss_index = faiss.read_index(settings.faiss_index_path)
        with open(settings.faiss_metadata_path, "r") as f:
            _metadata = json.load(f)
        bm25_path = settings.faiss_index_path + "_bm25.pkl"
        if os.path.exists(bm25_path):
            with open(bm25_path, "rb") as f:
                _bm25_index = pickle.load(f)
        logger.info("Index loaded", chunks=len(_metadata))
        return True
    return False

def ingest_pdf(pdf_path: str) -> Dict:
    global _faiss_index, _metadata, _bm25_index

    logger.info("Starting ingestion", file=pdf_path)

    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_documents(pages)
    texts = [c["text"] for c in chunks]

    logger.info("Embedding chunks", count=len(chunks))
    embeddings = embed_texts(texts)

    new_index = build_faiss_index(embeddings)

    tokenized = [t.lower().split() for t in texts]
    bm25 = BM25Okapi(tokenized)

    _faiss_index = new_index
    _metadata = chunks
    _bm25_index = bm25

    save_index(new_index, chunks, bm25)

    return {
        "status": "success",
        "chunks_created": len(chunks),
        "source": Path(pdf_path).name
    }

def get_index_state():
    return _faiss_index, _metadata, _bm25_index
