import numpy as np
from typing import List, Dict, Tuple
from app.core.config import settings
from app.services.ingestion import embed_texts, get_index_state

def dense_search(query: str, top_k: int) -> List[Tuple[int, float]]:
    """FAISS dense retrieval."""
    index, metadata, _ = get_index_state()
    if index is None or len(metadata) == 0:
        return []

    q_emb = embed_texts([query])
    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            results.append((int(idx), float(score)))
    return results

def bm25_search(query: str, top_k: int) -> List[Tuple[int, float]]:
    """BM25 sparse retrieval."""
    _, metadata, bm25_index = get_index_state()
    if bm25_index is None:
        return []

    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(int(i), float(scores[i])) for i in top_indices if scores[i] > 0]

def hybrid_search(query: str) -> List[Dict]:
    """
    Reciprocal Rank Fusion (RRF) combining dense + BM25.
    This is what MNCs expect: not just cosine similarity alone.
    """
    _, metadata, _ = get_index_state()
    if not metadata:
        return []

    k = 60  # RRF constant
    rrf_scores = {}

    # Dense results
    dense_results = dense_search(query, settings.top_k_dense)
    for rank, (idx, _) in enumerate(dense_results):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

    # BM25 results
    bm25_results = bm25_search(query, settings.top_k_bm25)
    for rank, (idx, _) in enumerate(bm25_results):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

    # Sort by RRF score
    sorted_indices = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    # Build result dicts
    results = []
    for idx, score in sorted_indices[:settings.top_k_dense]:
        if 0 <= idx < len(metadata):
            chunk = metadata[idx].copy()
            chunk["retrieval_score"] = round(score, 4)
            results.append(chunk)

    return results