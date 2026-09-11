# 🚂 Conversational IVR Modernization — Train Enquiry System

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Tests: Passing](https://img.shields.io/badge/Tests-10%2F10%20Passed-success.svg)](#-testing)

A complete, production-ready **Conversational IVR Modernization Framework** designed to transform traditional DTMF (keypad-only) telephony IVR systems into an AI-driven, speech-enabled conversational assistant for train enquiry and passenger support services.

---

## 🌟 Overview & Problem Solved

Traditional Interactive Voice Response (IVR) systems rely heavily on rigid touch-tone keypads (DTMF), rigid visual menus, and deep nested branching. Callers often struggle with long voice prompts, rigid navigation paths, and lack of flexibility.

This project **modernizes legacy IVR architectures** by introducing:
1. **Dual Interaction Model**: Seamlessly handles both keypad (DTMF 0-9, *, #) and natural speech inputs.
2. **Intent Recognition & NLP**: Uses pattern-matching, fuzzy string distance scoring, and entity extraction to understand user queries such as *"I want to book a ticket for tomorrow"* or *"Check status of train 12718"*.
3. **Dynamic State-Machine Engine**: JSON-driven flow transitions supporting over 10 distinct railway enquiry services with automatic state recovery and context collection.
4. **Interactive Web Simulator**: Full-featured browser UI simulating call control, real-time timer, Web Speech API (STT & TTS), call history, and downloadable JSON transcripts.

---

## ✨ Key Features

- 🎙️ **Speech & Voice Control**: Native Web Speech API integration for speech-to-text (STT) and text-to-speech (TTS) with speech interruption support.
- 🔢 **Keypad (DTMF) Simulation**: Full phone keypad (0–9, *, #) with instant state transitions.
- 🧠 **Intelligent NLP Engine**: Recognizes user intent, extracts 5-digit train numbers, 10-digit PNRs, and travel classes even with colloquial phrasing.
- 🔄 **10+ Modular Enquiry Flows**:
  - 🎟️ Ticket Booking & Class Selection
  - 📍 Live Train Running Status
  - 🕒 Train Schedules & Timings
  - ❌ Ticket Cancellation & Refund Calculation
  - 🔍 PNR Status Lookup
  - 💺 Seat Availability Engine
  - 💰 Fare Calculation Enquiry
  - 🚉 Trains Between Stations Search
  - 🎧 Customer Support Agent Handoff
- 📊 **Session & Call Logging**: In-memory session handling with persistent JSON call transcript generation (`backend/logs/`).
- 🧪 **100% Verified Test Suite**: Automated Pytest unit test coverage for FastAPI endpoints, health checks, and state transitions.

---

## 🏗️ Architecture & Technology Stack

### System Architecture

```
                               ┌──────────────────────────────────────────┐
                               │       Frontend (Browser Simulator)       │
                               │  - Web Speech API (STT & TTS)            │
                               │  - Interactive Keypad & Timer            │
                               │  - Call History & Transcript Export      │
                               └────────────────────┬─────────────────────┘
                                                    │ REST API
                                                    ▼
                               ┌──────────────────────────────────────────┐
                               │           FastAPI Backend Server         │
                               │  - Route Handlers (/api/ivr/*, /health)  │
                               │  - In-Memory Session Storage             │
                               └──────────────┬──────────────┬────────────┘
                                              │              │
                                              ▼              ▼
                              ┌──────────────────┐  ┌──────────────────┐
                              │   Flow Manager   │  │    NLP Engine    │
                              │ (JSON State Machine)│(Intent & Entity) │
                              └──────────────┬───┘  └──────────────────┘
                                             │
                                             ▼
                              ┌────────────────────────────────┐
                              │ backend/flows/*.json           │
                              │ (10 Service Flow Definitions)  │
                              └────────────────────────────────┘
```

### Tech Stack
- **Backend Framework**: Python 3.9+, FastAPI, Uvicorn, Pydantic
- **Frontend**: Plain HTML5, Modern Vanilla CSS3, ES6 JavaScript
- **NLP Engine**: Custom pattern matching, Difflib `SequenceMatcher`, regex entity extractors
- **Testing**: Pytest, Pytest-Asyncio, HTTPX AsyncClient

---

## 📂 Folder Structure

```
ivr-modern/
├── backend/
│   ├── main.py                 # FastAPI application entry point & session routes
│   ├── flows/                  # JSON-based IVR state definitions
│   │   ├── train_main.json     # Main menu flow
│   │   ├── booking.json        # Ticket booking flow
│   │   ├── status.json         # Train running status flow
│   │   ├── schedule.json       # Train schedule flow
│   │   ├── cancellation.json   # Cancellation & refund flow
│   │   ├── pnr_status.json     # PNR status flow
│   │   ├── seat_availability.json # Seat availability flow
│   │   ├── fare_enquiry.json   # Fare enquiry flow
│   │   ├── train_between_stations.json # Route finder flow
│   │   └── agent.json          # Customer support agent handoff
│   ├── utils/
│   │   ├── flow_manager.py     # State machine & transition processing engine
│   │   └── advanced_nlp.py     # Intent recognition & entity extraction engine
│   └── logs/                   # Auto-generated JSON call summaries
├── frontend/
│   ├── index.html              # Interactive IVR Simulator UI
│   ├── script.js               # Web Speech API, Keypad & Fetch integration
│   └── style.css               # Responsive design & theme
├── test_api.py                 # Sync Pytest endpoint test suite
├── test_api_endpoints.py       # Async HTTPX endpoint test suite
├── test_flow_manager.py        # State machine unit tests
├── conftest.py                 # Pytest fixtures & environment setup
├── requirements.txt            # Python dependencies
├── .env.example                # Sample configuration environment variables
├── Dockerfile                  # Containerization dockerfile
├── Procfile                    # Deployment process configuration
├── .gitignore                  # Git repository exclusion rules
├── LICENSE.md                  # License file
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python 3.9+** installed
- **Modern Web Browser** (Google Chrome or Microsoft Edge recommended for Web Speech API support)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/praveen131106/ivr-modern.git
   cd ivr-modern
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Configure environment:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

---

## 💻 Running the Application

### 1. Start the Backend API Server

Using Python directly:
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```

Or using the startup script (Windows):
```bash
start_backend.bat
```

Or using the startup script (Linux/Mac):
```bash
chmod +x start_backend.sh
./start_backend.sh
```

The backend server will be live at `http://localhost:8000`. You can inspect interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 2. Launch the Frontend IVR Simulator

Open `frontend/index.html` directly in your browser, or launch a simple local HTTP server:

```bash
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080` in your web browser.

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API description & available endpoints |
| `GET` | `/health` | Server health check, uptime, & active session metrics |
| `POST` | `/api/ivr/start` | Initialize a new IVR call session |
| `POST` | `/api/ivr/input` | Send user keypad or speech input to process next state |
| `POST` | `/api/ivr/end` | Terminate session & generate call summary transcript |
| `GET` | `/api/flows` | List loaded IVR flow definitions |
| `GET` | `/api/session/{id}` | Inspect active session state (debugging) |

### Example Input Request (`POST /api/ivr/input`)
```json
{
  "session_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "input": "book a ticket for train 12718"
}
```

---

## 🧪 Testing

The repository includes a 100% passing test suite built with `pytest` and `httpx`.

Run all unit tests:
```bash
pytest -v
```

Expected Output:
```
test_api.py::test_healthcheck_endpoint PASSED                            [ 10%]
test_api.py::test_session_lifecycle PASSED                               [ 20%]
test_api.py::test_invalid_session_rejected PASSED                        [ 30%]
test_api.py::test_flows_listing PASSED                                   [ 40%]
test_api_endpoints.py::test_root_endpoint[asyncio] PASSED                [ 50%]
test_api_endpoints.py::test_session_lifecycle[asyncio] PASSED            [ 60%]
test_api_endpoints.py::test_healthcheck[asyncio] PASSED                  [ 70%]
test_flow_manager.py::test_flows_are_loaded PASSED                       [ 80%]
test_flow_manager.py::test_keypad_transition_to_booking PASSED           [ 90%]
test_flow_manager.py::test_invalid_input_recovers PASSED                 [100%]

======================== 10 passed in 0.18s ========================
```

---

## ⚙️ Known Limitations & Future Improvements

- **In-Memory Sessions**: Sessions are currently stored in-memory. For multi-node production setups, a Redis session store can be integrated.
- **Web Speech API Browser Dependency**: Voice recognition relies on browser Web Speech API capabilities. Integrating WebSockets with a server-side speech engine (e.g. Whisper / Vosk) would enable headless voice calls.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE.md).

## 👤 Author

**Praveen**
- GitHub: [@praveen131106](https://github.com/praveen131106)
- Repository: [ivr-modern](https://github.com/praveen131106/ivr-modern)
