"""
Test Script: One-Shot Spoken Booking & Slot-Filling Verification
Verifies that single-sentence spoken requests ("I want to book an AC ticket for Godavari Express",
"Book sleeper ticket on 12718", "Book AC ticket", etc.) immediately fill slots, confirm booking, and generate PNRs.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

client = TestClient(app)

def test_one_shot_and_multiturn_bookings():
    print("=" * 70)
    print("TESTING ONE-SHOT & MULTI-TURN SPOKEN BOOKING WORKFLOWS")
    print("=" * 70)

    # 1. Full 1-Shot Spoken Sentence from Main Menu
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    r1 = client.post("/api/ivr/input", json={"session_id": sid, "input": "I want to book an AC ticket for Godavari Express"})
    msg1 = r1.json()["message"]
    print("\n1-Shot Spoken Sentence Result:")
    print("User: 'I want to book an AC ticket for Godavari Express'")
    print("System Response:", msg1)

    assert "confirmed" in msg1.lower() or "booked" in msg1.lower(), f"1-Shot booking failed: {r1.json()}"
    assert "PNR" in msg1 or "pnr" in msg1.lower(), f"Missing PNR in 1-shot booking: {msg1}"
    assert "AC" in msg1 and ("Godavari" in msg1 or "12718" in msg1), f"Slot mapping error: {msg1}"
    print("[PASS] 1-Shot Spoken Booking (Instant PNR in 1 Turn) PASSED!")

    # 2. 1-Shot Spoken Sentence with Digit Train Number
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    r2 = client.post("/api/ivr/input", json={"session_id": sid, "input": "Book sleeper ticket for train 12718"})
    msg2 = r2.json()["message"]
    assert "confirmed" in msg2.lower() and "PNR" in msg2 and "Sleeper" in msg2, f"1-Shot digit booking failed: {r2.json()}"
    print("[PASS] 1-Shot Spoken Booking with Train 12718 PASSED!")

    # 3. 2-Shot Spoken Booking (Class provided first, then Train Name)
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    r3_a = client.post("/api/ivr/input", json={"session_id": sid, "input": "Book an AC ticket"})
    print("\n2-Shot Spoken Booking (Turn 1):", r3_a.json()["message"])
    assert "collect_train_number" in r3_a.json()["state"] or "train" in r3_a.json()["message"].lower()

    r3_b = client.post("/api/ivr/input", json={"session_id": sid, "input": "Godavari Express"})
    msg3_b = r3_b.json()["message"]
    print("2-Shot Spoken Booking (Turn 2):", msg3_b)
    assert "confirmed" in msg3_b.lower() and "PNR" in msg3_b and "Godavari" in msg3_b, f"2-Shot booking failed: {r3_b.json()}"
    print("[PASS] 2-Shot Spoken Booking (Class first -> Train second) PASSED!")

    # 4. 2-Shot Spoken Booking (Train Name provided first, then Class)
    res = client.post("/api/ivr/start")
    sid = res.json()["session_id"]
    r4_a = client.post("/api/ivr/input", json={"session_id": sid, "input": "Book ticket for Godavari Express"})
    print("\n2-Shot Spoken Booking (Train first, Turn 1):", r4_a.json()["message"])
    assert "select_class" in r4_a.json()["state"] or "class" in r4_a.json()["message"].lower()

    r4_b = client.post("/api/ivr/input", json={"session_id": sid, "input": "Tatkal"})
    msg4_b = r4_b.json()["message"]
    print("2-Shot Spoken Booking (Turn 2):", msg4_b)
    assert "confirmed" in msg4_b.lower() and "PNR" in msg4_b and "Tatkal" in msg4_b, f"2-Shot train-first failed: {r4_b.json()}"
    print("[PASS] 2-Shot Spoken Booking (Train first -> Class second) PASSED!")

    print("=" * 70)
    print("ALL SPOKEN BOOKING WORKFLOW VARIATIONS VERIFIED 100% WORKING!")
    print("=" * 70)

if __name__ == "__main__":
    test_one_shot_and_multiturn_bookings()
