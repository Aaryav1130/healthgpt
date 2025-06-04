import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

def test_chunk_documents_basic():
    from app.utils.chunker import chunk_documents
    pages = [
        {
            "page_num": 1,
            "text": "Hypertension is high blood pressure. It is a common condition. Treatment includes medication and lifestyle changes.",
            "source": "test.pdf",
            "total_pages": 1
        }
    ]
    chunks = chunk_documents(pages)
    assert len(chunks) > 0
    assert "text" in chunks[0]
    assert "source" in chunks[0]
    assert chunks[0]["source"] == "test.pdf"

def test_chunk_documents_empty():
    from app.utils.chunker import chunk_documents
    result = chunk_documents([])
    assert result == []

def test_chunk_has_required_fields():
    from app.utils.chunker import chunk_documents
    pages = [{
        "page_num": 1,
        "text": "Diabetes mellitus is a metabolic disease. " * 20,
        "source": "diabetes.pdf",
        "total_pages": 5
    }]
    chunks = chunk_documents(pages)
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "source" in chunk
        assert "page_num" in chunk