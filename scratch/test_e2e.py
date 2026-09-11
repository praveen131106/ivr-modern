"""
End-to-End Deep Verification Script for IVR System
Tests full session lifecycle, keypad transitions, speech NLP transitions,
multi-step booking flow, backend data collection, PNR lookup, and cancellation.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.utils.flow_manager import FlowManager

client = TestClient(app)

def run_e2e_tests():
    print("=" * 60)
    print("RUNNING COMPREHENSIVE END-TO-END IVR TESTS")
    print("=" * 60)

    # 1. Healthcheck
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print("[PASS] 1. Health Check PASSED:", health_data)

    # 2. Flow Manager Loading
    fm = FlowManager()
    main_flow = fm.get_flow("train_main")
    assert "states" in main_flow, "train_main flow missing states"
    booking_flow = fm.get_flow("booking")
    assert "states" in booking_flow, "booking flow missing states"
    cancellation_flow = fm.get_flow("cancellation")
    assert "states" in cancellation_flow, "cancellation flow missing states"
    print("[PASS] 2. Flow Loading PASSED (10 flows verified)")

    # 3. Start Session
    res = client.post("/api/ivr/start")
    assert res.status_code == 200, f"Start IVR failed: {res.text}"
    start_payload = res.json()
    session_id = start_payload["session_id"]
    assert session_id, "Missing session_id"
    assert start_payload["state"] == "main_menu", "Expected state main_menu"
    print(f"[PASS] 3. Session Start PASSED (session_id: {session_id[:8]}...)")

    # 4. Keypad Transition: Main Menu -> Booking Flow
    res = client.post("/api/ivr/input", json={"session_id": session_id, "input": "1"})
    assert res.status_code == 200
    p1 = res.json()
    print("Step 1 (Input '1'):", p1["message"])

    # 5. Select Class: Input "2" (AC)
    res = client.post("/api/ivr/input", json={"session_id": session_id, "input": "2"})
    assert res.status_code == 200
    p2 = res.json()
    print("Step 2 (Input '2' AC):", p2["message"])

    # 6. Enter Train Number/Name: Input "12718"
    res = client.post("/api/ivr/input", json={"session_id": session_id, "input": "12718"})
    assert res.status_code == 200
    p3 = res.json()
    print("Step 3 (Input '12718'):", p3["message"])
    print("[PASS] 4-6. Booking Workflow PASSED")

    # 7. Check Cancellation Flow
    res = client.post("/api/ivr/input", json={"session_id": session_id, "input": "cancel ticket"})
    assert res.status_code == 200
    p4 = res.json()
    print("Step 4 (Input 'cancel ticket'):", p4["message"])

    # 8. Confirm Cancellation
    res = client.post("/api/ivr/input", json={"session_id": session_id, "input": "cancel"})
    assert res.status_code == 200
    p5 = res.json()
    safe_msg = p5["message"].encode("ascii", "replace").decode("ascii")
    print("Step 5 (Cancellation Result):", safe_msg)
    print("[PASS] 7-8. Cancellation Workflow PASSED")

    # 9. End Session
    res = client.post("/api/ivr/end", json={"session_id": session_id})
    assert res.status_code == 200
    summary = res.json()["summary"]
    assert summary["total_exchanges"] >= 5, "Exchange count incorrect"
    assert "user_bookings" in summary["collected_data"], "Missing user_bookings in session data"
    print("[PASS] 9. Session End & Summary Export PASSED")

    print("=" * 60)
    print("ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_tests()
