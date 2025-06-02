from typing import List, Dict
from sentence_transformers import CrossEncoder
from app.core.config import settings
from app.core.logging import logger

_reranker: CrossEncoder = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        logger.info("Loading reranker", model=settings.reranker_model)
        _reranker = CrossEncoder(
            settings.reranker_model,
            max_length=512,
            device="cpu"
        )
    return _reranker

def rerank(query: str, candidates: List[Dict]) -> List[Dict]:
    """
    Cross-encoder reranking: more accurate than embedding similarity alone.
    This is the architecture step that separates junior from senior ML engineers.
    """
    if not candidates:
        return []

    reranker = get_reranker()
    pairs = [(query, c["text"]) for c in candidates]

    scores = reranker.predict(pairs, show_progress_bar=False)

    for chunk, score in zip(candidates, scores):
        chunk["rerank_score"] = round(float(score), 4)

    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:settings.top_k_rerank]