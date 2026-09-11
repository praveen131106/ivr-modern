"""
Test Script: Direct Train Number / Pill Input Booking Flow Verification
Verifies that entering a train number or name directly at main menu (or clicking train pills)
automatically initiates booking, prompts for class, and confirms booking with a PNR.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

client = TestClient(app)

def test_direct_train_pill_booking():
    print("=" * 70)
    print("TESTING DIRECT TRAIN NUMBER / PILL INPUT BOOKING FLOW")
    print("=" * 70)

    # 1. Direct Train Pill Click '12718' at Main Menu
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]

    r1 = client.post("/api/ivr/input", json={"session_id": sid, "input": "12718"})
    msg1 = r1.json()["message"]
    print("\nStep 1 (Input '12718' at Main Menu):", msg1)
    assert "class" in msg1.lower() or "sleeper" in msg1.lower() or "12718" in msg1, f"Failed train pill transition: {r1.json()}"
    print("[PASS] Direct Train Number '12718' successfully initiated booking & class prompt!")

    r2 = client.post("/api/ivr/input", json={"session_id": sid, "input": "AC"})
    msg2 = r2.json()["message"]
    print("Step 2 (Input 'AC'):", msg2)
    assert "confirmed" in msg2.lower() and "PNR" in msg2 and "12718" in msg2, f"Failed PNR generation: {r2.json()}"
    print("[PASS] Direct Train Pill Booking Completed with PNR!")

    # 2. Direct Train Name 'Godavari Express' at Main Menu
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]

    r1_name = client.post("/api/ivr/input", json={"session_id": sid, "input": "Godavari Express"})
    msg1_name = r1_name.json()["message"]
    print("\nStep 1 (Input 'Godavari Express' at Main Menu):", msg1_name)
    assert "class" in msg1_name.lower() or "sleeper" in msg1_name.lower(), f"Failed train name transition: {r1_name.json()}"
    print("[PASS] Direct Train Name 'Godavari Express' successfully initiated booking & class prompt!")

    r2_name = client.post("/api/ivr/input", json={"session_id": sid, "input": "Sleeper"})
    msg2_name = r2_name.json()["message"]
    print("Step 2 (Input 'Sleeper'):", msg2_name)
    assert "confirmed" in msg2_name.lower() and "PNR" in msg2_name and "Godavari" in msg2_name, f"Failed PNR generation: {r2_name.json()}"
    print("[PASS] Direct Train Name Booking Completed with PNR!")

    print("=" * 70)
    print("ALL DIRECT TRAIN NUMBER & NAME BOOKING TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_direct_train_pill_booking()
