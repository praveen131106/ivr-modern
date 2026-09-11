import urllib.request
import json
import sys

BASE_URL = 'http://127.0.0.1:8000'

def start_session():
    req = urllib.request.Request(f'{BASE_URL}/api/ivr/start', method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['session_id']

def send_input(session_id, user_text):
    payload = json.dumps({'session_id': session_id, 'input': user_text}).encode()
    req = urllib.request.Request(f'{BASE_URL}/api/ivr/input', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

trains = [
    ("12718", "Godavari Express"),
    ("17018", "Secunderabad Express"),
    ("12009", "Shatabdi Express"),
    ("12345", "Rajdhani Express")
]

classes = ["Sleeper", "AC", "Tatkal"]

print("=== STARTING COMPREHENSIVE 4-TRAIN WORKFLOW VALIDATION ===")

for train_num, train_name in trains:
    for cls in classes:
        print(f"\n--- Testing Sequential Booking: {train_name} ({train_num}) | Class: {cls} ---")
        sid = start_session()
        
        # Step 1: Book intent
        r1 = send_input(sid, "Book a train")
        assert r1['state'] == 'select_class', f"Expected select_class, got {r1['state']}"
        print("  [Pass] Step 1 -> Prompted for class")

        # Step 2: Class selection
        r2 = send_input(sid, cls)
        assert r2['state'] == 'collect_train_number', f"Expected collect_train_number, got {r2['state']}"
        print(f"  [Pass] Step 2 -> Selected {cls}, prompted for train")

        # Step 3: Train selection
        train_input = train_name if cls == "Sleeper" else train_num
        r3 = send_input(sid, train_input)
        assert "PNR" in r3['message'] or "confirmed" in r3['message'].lower(), f"Expected booking confirmation, got: {r3['message']}"
        print(f"  [Pass] Step 3 -> Confirmed booking for {train_input}: {r3['message'][:90]}...")

print("\n--- Testing Subflows across 4 trains ---")

for train_num, train_name in trains:
    # Status
    sid = start_session()
    r = send_input(sid, f"Status of {train_name}")
    assert train_num in r['message'] or train_name.lower() in r['message'].lower(), f"Status failed for {train_name}"
    print(f"  [Pass] Status for {train_name}: {r['message'][:80]}...")

    # Schedule
    sid = start_session()
    r = send_input(sid, f"Schedule for train {train_num}")
    assert train_num in r['message'] or train_name.lower() in r['message'].lower(), f"Schedule failed for {train_num}"
    print(f"  [Pass] Schedule for {train_num}: {r['message'][:80]}...")

    # Availability
    sid = start_session()
    r = send_input(sid, f"Seat availability for {train_name}")
    assert "Available" in r['message'] or "Seat" in r['message'] or "availability" in r['message'].lower(), f"Availability failed for {train_name}"
    print(f"  [Pass] Availability for {train_name}: {r['message'][:80]}...")

    # Fare
    sid = start_session()
    r = send_input(sid, f"Fare for train {train_num}")
    assert "Fare" in r['message'] or "₹" in r['message'] or "Rs" in r['message'], f"Fare failed for {train_num}"
    clean_msg = r['message'][:80].replace("₹", "Rs.")
    print(f"  [Pass] Fare for {train_num}: {clean_msg}...")

print("\n=== ALL 4-TRAIN COMPREHENSIVE WORKFLOW TESTS PASSED PERFECTLY ===")
