import pytest


@pytest.mark.anyio
async def test_root_endpoint(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Train IVR System API"
    assert "/api/ivr/start" in payload["endpoints"]


@pytest.mark.anyio
async def test_session_lifecycle(async_client):
    start_response = await async_client.post("/api/ivr/start", json={})
    assert start_response.status_code == 200
    start_payload = start_response.json()
    session_id = start_payload["session_id"]
    assert session_id
    assert start_payload["state"] == "main_menu"

    input_response = await async_client.post(
        "/api/ivr/input",
        json={"session_id": session_id, "input": "1"},
    )
    assert input_response.status_code == 200
    input_payload = input_response.json()
    assert input_payload["session_id"] == session_id
    assert input_payload["message"]

    end_response = await async_client.post(
        "/api/ivr/end",
        json={"session_id": session_id},
    )
    assert end_response.status_code == 200
    summary = end_response.json()["summary"]
    assert summary["session_id"] == session_id
    assert summary["total_exchanges"] >= 1


@pytest.mark.anyio
async def test_healthcheck(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["active_sessions"] >= 0

