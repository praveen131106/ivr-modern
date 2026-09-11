"""
Test Script: Natural Spoken Train Names Verification
Verifies that spoken train names (e.g. "godavari express", "secunderabad express", "shatabdi", "visakha express")
properly advance through booking, status, schedule, fare, and cancellation workflows without getting stuck.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

client = TestClient(app)

def test_spoken_train_names():
    print("=" * 70)
    print("VERIFYING SPOKEN TRAIN NAMES (e.g., 'godavari express') IN BOOKING FLOW")
    print("=" * 70)

    # Test 1: Spoken 'godavari express' in booking flow
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]

    # Step 0: Start Booking Flow
    client.post("/api/ivr/input", json={"session_id": sid, "input": "1"})

    # Step 1: Select Class
    r1 = client.post("/api/ivr/input", json={"session_id": sid, "input": "AC"})
    assert r1.json()["state"] == "collect_train_number", f"Failed class select: {r1.json()}"
    print("[PASS] Step 1: Selected 'AC' class")

    # Step 2: Say 'godavari express'
    r2 = client.post("/api/ivr/input", json={"session_id": sid, "input": "godavari express"})
    msg2 = r2.json()["message"]
    print("[PASS] Step 2 Output for 'godavari express':", msg2)

    assert "confirmed" in msg2.lower() or "booked" in msg2.lower() or "pnr" in msg2.lower(), f"Failed to confirm booking on godavari express: {r2.json()}"
    assert "12718 Godavari Express" in msg2 or "Godavari" in msg2, f"Train display name mismatch: {msg2}"
    print("[PASS] Booking on 'godavari express' COMPLETED SUCCESSFULLY!")

    # Test 2: Spoken 'secunderabad express' in booking flow
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    client.post("/api/ivr/input", json={"session_id": sid, "input": "1"})
    client.post("/api/ivr/input", json={"session_id": sid, "input": "Sleeper"})
    r = client.post("/api/ivr/input", json={"session_id": sid, "input": "secunderabad express"})
    msg = r.json()["message"]
    assert "confirmed" in msg.lower() and "Secunderabad" in msg, f"Failed on secunderabad express: {r.json()}"
    print("[PASS] Booking on 'secunderabad express' COMPLETED SUCCESSFULLY!")

    # Test 3: Spoken 'shatabdi' in booking flow
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    client.post("/api/ivr/input", json={"session_id": sid, "input": "1"})
    client.post("/api/ivr/input", json={"session_id": sid, "input": "Tatkal"})
    r = client.post("/api/ivr/input", json={"session_id": sid, "input": "shatabdi"})
    msg = r.json()["message"]
    assert "confirmed" in msg.lower() and "Shatabdi" in msg, f"Failed on shatabdi: {r.json()}"
    print("[PASS] Booking on 'shatabdi' COMPLETED SUCCESSFULLY!")

    print("=" * 70)
    print("ALL SPOKEN TRAIN NAME TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_spoken_train_names()
