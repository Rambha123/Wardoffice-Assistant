"""Smoke test: confirms the FastAPI app boots and /api/health responds."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# TODO: add tests per module as they're implemented:
#   - test_chat.py       (mock llm_service + retrieval_service)
#   - test_checklist.py  (test conditional logic with a fixture Service)
#   - test_readiness.py  (mock ocr_service, assert temp files are deleted)
