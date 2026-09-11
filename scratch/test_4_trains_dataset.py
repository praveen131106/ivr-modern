"""
Test Script: 4 Core Trains Full Dataset & Step-by-Step Workflow Verification
Tests complete data and natural workflows for 4 core trains:
12718 Godavari Express, 17018 Secunderabad Express, 12009 Shatabdi Express, 12345 Rajdhani Express.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

client = TestClient(app)

def test_4_core_trains_dataset():
    print("=" * 70)
    print("VERIFYING COMPLETE DATASET & STEP-BY-STEP WORKFLOWS FOR 4 CORE TRAINS")
    print("=" * 70)

    trains = [
        ("12718", "Godavari Express"),
        ("17018", "Secunderabad Express"),
        ("12009", "Shatabdi Express"),
        ("12345", "Rajdhani Express")
    ]

    for num, name in trains:
        print(f"\n--- Testing Train {num} ({name}) ---")
        
        # 1. Step-by-step Sequential Booking Workflow
        res = client.post("/api/ivr/start")
        sid = res.json()["session_id"]
        
        # Step A: Intent to book
        r_a = client.post("/api/ivr/input", json={"session_id": sid, "input": "1"}) # Keypad 1 -> Book ticket
        assert r_a.json()["state"] == "select_class", f"Step A failed for {num}: {r_a.json()}"
        
        # Step B: Select Class (AC)
        r_b = client.post("/api/ivr/input", json={"session_id": sid, "input": "2"}) # Keypad 2 -> AC
        assert r_b.json()["state"] == "collect_train_number", f"Step B failed for {num}: {r_b.json()}"
        
        # Step C: Enter Train Number/Name
        r_c = client.post("/api/ivr/input", json={"session_id": sid, "input": num})
        msg_c = r_c.json()["message"]
        assert "confirmed" in msg_c.lower() and "PNR" in msg_c and (num in msg_c or name in msg_c), f"Step C failed for {num}: {msg_c}"
        print(f"[PASS] Booking Workflow for Train {num} ({name}): Confirmed with PNR!")

        # 2. Live Running Status
        res_st = client.post("/api/ivr/start")
        sid_st = res_st.json()["session_id"]
        client.post("/api/ivr/input", json={"session_id": sid_st, "input": "2"}) # Status
        r_status = client.post("/api/ivr/input", json={"session_id": sid_st, "input": num})
        msg_status = r_status.json()["message"]
        assert num in msg_status or name in msg_status, f"Status failed for {num}: {msg_status}"
        print(f"[PASS] Live Status for Train {num} ({name}): {msg_status[:60]}...")

        # 3. Train Schedule Information
        res_sc = client.post("/api/ivr/start")
        sid_sc = res_sc.json()["session_id"]
        client.post("/api/ivr/input", json={"session_id": sid_sc, "input": "3"}) # Schedule
        r_sched = client.post("/api/ivr/input", json={"session_id": sid_sc, "input": num})
        msg_sched = r_sched.json()["message"]
        assert num in msg_sched or name in msg_sched or "departs" in msg_sched.lower(), f"Schedule failed for {num}: {msg_sched}"
        print(f"[PASS] Schedule Info for Train {num} ({name}): {msg_sched[:60]}...")

    print("\n" + "=" * 70)
    print("ALL 4 CORE TRAINS VERIFIED 100% WORKING WITH COMPLETE DATASET!")
    print("=" * 70)

if __name__ == "__main__":
    test_4_core_trains_dataset()
