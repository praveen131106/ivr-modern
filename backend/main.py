"""
FastAPI Backend for Conversational IVR Train Enquiry System

Author: Praveen
Project: Conversational IVR Modernization
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json
from datetime import datetime
import sys
import os

# Ensure backend/utils is always importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UTILS_DIR = os.path.join(BASE_DIR, "utils")

if UTILS_DIR not in sys.path:
    sys.path.append(UTILS_DIR)

from flow_manager import FlowManager

app = FastAPI(title="Train IVR System", version="1.0.0")

# ✅ UPDATED CORS SETTINGS (IMPORTANT FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agent-696b2e3331a00135477f9a30--moder-ivr-a.netlify.app",
        "https://moder-ivr-a.netlify.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions: Dict[str, Dict[str, Any]] = {}

# Initialize flow manager
flow_manager = FlowManager()

def reload_flows():
    flow_manager.reload_flows()

# Pydantic models
class IVRStartRequest(BaseModel):
    pass

class IVRInputRequest(BaseModel):
    session_id: str
    input: str

class IVREndRequest(BaseModel):
    session_id: str

class IVRResponse(BaseModel):
    session_id: str
    message: str
    state: str
    options: Optional[Dict[str, str]] = None
    is_end: bool = False

def get_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

@app.get("/")
async def root():
    return {
        "message": "Train IVR System API",
        "version": "1.0.0",
        "endpoints": {
            "/api/ivr/start": "Start new IVR session",
            "/api/ivr/input": "Process user input",
            "/api/ivr/end": "End IVR session",
            "/api/flows": "Get available flows"
        }
    }

@app.post("/api/ivr/start", response_model=IVRResponse)
async def start_ivr(request: IVRStartRequest = None):
    session_id = str(uuid.uuid4())
    greeting = get_greeting()

    sessions[session_id] = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "current_flow": "train_main",
        "current_state": "main_menu",
        "history": [],
        "data": {}
    }

    flow_manager.reload_flows()

    main_flow = flow_manager.get_flow("train_main")
    main_menu = main_flow.get("states", {}).get("main_menu", {})

    welcome_message = f"{greeting}! Thank you for calling the Train Enquiry System. "
    menu_message = main_menu.get("message", "")

    if menu_message:
        full_message = welcome_message + menu_message
    else:
        full_message = welcome_message + "Press 1 for Booking, Press 2 for Status, Press 3 for Schedule."

    sessions[session_id]["history"].append({
        "type": "system",
        "message": full_message,
        "timestamp": datetime.now().isoformat()
    })

    menu_options = main_menu.get("options", {
        "1": "Book Train Ticket",
        "2": "Check Train Status",
        "3": "Train Schedule",
        "4": "Ticket Cancellation",
        "5": "PNR Status",
        "6": "Seat Availability",
        "7": "Fare Enquiry",
        "8": "Trains Between Stations",
        "9": "Customer Support",
        "0": "Repeat Menu",
        "*": "Main Menu",
        "#": "Confirm"
    })

    return IVRResponse(
        session_id=session_id,
        message=full_message,
        state="main_menu",
        options=menu_options,
        is_end=False
    )

@app.post("/api/ivr/input", response_model=IVRResponse)
async def process_input(request: IVRInputRequest):

    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    user_input = request.input.strip().lower()

    session["history"].append({
        "type": "user",
        "message": user_input,
        "timestamp": datetime.now().isoformat()
    })

    current_flow = flow_manager.get_flow(session["current_flow"])
    current_state = session["current_state"]

    is_keypad = len(user_input) == 1 and user_input in "0123456789*#"

    try:
        next_state, response_message, options, is_end = flow_manager.process_input(
            current_flow,
            current_state,
            user_input,
            is_keypad,
            session
        )
    except Exception as e:
        print("Error:", e)
        response_message = "Something went wrong. Please try again."
        next_state = current_state
        options = {}
        is_end = False

    session["current_state"] = next_state

    session["history"].append({
        "type": "system",
        "message": response_message,
        "timestamp": datetime.now().isoformat()
    })

    return IVRResponse(
        session_id=request.session_id,
        message=response_message,
        state=next_state,
        options=options,
        is_end=is_end
    )

@app.post("/api/ivr/end")
async def end_ivr(request: IVREndRequest):

    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    session["ended_at"] = datetime.now().isoformat()

    summary = {
        "session_id": request.session_id,
        "started_at": session["started_at"],
        "ended_at": session["ended_at"],
        "transcript": session["history"],
        "collected_data": session["data"]
    }

    try:
        with open(f"backend/logs/call_{request.session_id}.json", "w") as f:
            json.dump(summary, f, indent=2)
    except:
        pass

    return {
        "message": "Call ended successfully",
        "summary": summary
    }

@app.get("/api/flows")
async def get_flows():
    return {"available_flows": ["train_main", "booking", "status", "schedule"]}

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
