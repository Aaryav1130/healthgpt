import pytest
from unittest.mock import patch, MagicMock
import numpy as np

def test_hybrid_search_empty_index():
    """Should return empty list when no index is loaded."""
    from app.services.retriever import hybrid_search
    with patch("app.services.retriever.get_index_state", return_value=(None, [], None)):
        result = hybrid_search("what is hypertension?")
        assert result == []

def test_dense_search_empty():
    from app.services.retriever import dense_search
    with patch("app.services.retriever.get_index_state", return_value=(None, [], None)):
        result = dense_search("test query", top_k=5)
        assert result == []

def test_bm25_search_empty():
    from app.services.retriever import bm25_search
    with patch("app.services.retriever.get_index_state", return_value=(None, [], None)):
        result = bm25_search("test query", top_k=5)
        assert result == []

def test_rerank_empty_candidates():
    from app.services.reranker import rerank
    result = rerank("test query", [])
    assert result == []