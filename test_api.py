"""
Milestone 4 unit tests covering FastAPI IVR endpoints.
Run with: pytest milestone4/unit_tests
"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def start_session():
    response = client.post("/api/ivr/start")
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "main_menu"
    assert "session_id" in payload
    return payload


def test_healthcheck_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["uptime_seconds"] >= 0


def test_session_lifecycle():
    start_payload = start_session()
    session_id = start_payload["session_id"]

    input_payload = {
        "session_id": session_id,
        "input": "1",
    }
    response = client.post("/api/ivr/input", json=input_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["message"]

    end_payload = {"session_id": session_id}
    response = client.post("/api/ivr/end", json=end_payload)
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["session_id"] == session_id
    assert summary["total_exchanges"] >= 1


def test_invalid_session_rejected():
    payload = {"session_id": "invalid", "input": "1"}
    response = client.post("/api/ivr/input", json=payload)
    assert response.status_code == 404


def test_flows_listing():
    response = client.get("/api/flows")
    assert response.status_code == 200
    body = response.json()
    assert "available_flows" in body
    assert "train_main" in body["available_flows"]

