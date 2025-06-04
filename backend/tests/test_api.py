import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

def test_health_endpoint(client):
    """Health endpoint should always return 200."""
    with patch("app.api.routes.health.httpx.AsyncClient") as mock:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

def test_index_status_endpoint(client):
    """Index status should return chunk count."""
    response = client.get("/api/v1/documents/status")
    assert response.status_code == 200
    data = response.json()
    assert "index_loaded" in data
    assert "total_chunks" in data

def test_chat_requires_query(client):
    """Chat endpoint should reject empty query."""
    response = client.post("/api/v1/chat/stream", json={"query": ""})
    assert response.status_code == 422

def test_upload_rejects_non_pdf(client):
    """Upload should reject non-PDF files."""
    from io import BytesIO
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", BytesIO(b"not a pdf"), "text/plain")}
    )
    assert response.status_code == 400