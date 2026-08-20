from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
    assert "llm" in data["services"]


def test_error_envelope_format():
    response = client.get(
        "/v1/syllabus/jobs/non_existent_job_123",
        headers={"X-API-Key": "wml_dev_key_2026"},
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
    assert "message" in data["error"]

