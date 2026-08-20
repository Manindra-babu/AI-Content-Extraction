import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.job_service import JobManager, JobStatus

client = TestClient(app)


def test_unauthorized_without_api_key():
    response = client.get("/v1/question-bank/search")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_401"


def test_unauthorized_invalid_api_key():
    response = client.get("/v1/question-bank/search", headers={"X-API-Key": "invalid_key_xyz"})
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_401"


def test_authorized_valid_api_key():
    response = client.get("/v1/question-bank/search", headers={"X-API-Key": "wml_dev_key_2026"})
    assert response.status_code == 200


def test_rate_limiting_enforcement():
    # Make multiple rapid requests to trigger rate limit
    triggered_429 = False
    for i in range(70):
        res = client.get("/v1/usage", headers={"X-API-Key": "wml_test_ratelimit_key"})
        if res.status_code == 429:
            triggered_429 = True
            break

    assert triggered_429 is True


def test_job_manager_service():
    jm = JobManager()
    job = jm.create_job("job_100", "doc_100")
    assert job.job_id == "job_100"
    assert job.status == JobStatus.QUEUED

    updated = jm.update_job_status("job_100", JobStatus.DONE, progress=100.0)
    assert updated.status == JobStatus.DONE
    assert updated.completed_at is not None
