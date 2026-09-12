# 🚂 Conversational IVR Modernization — Train Enquiry System

[![Vercel Live Demo](https://img.shields.io/badge/Vercel-Live%20Demo-000000.svg?logo=vercel&logoColor=white)](https://ivr-modern.vercel.app/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Tests: Passing](https://img.shields.io/badge/Tests-10%2F10%20Passed-success.svg)](#-testing)

A complete, production-ready **Conversational IVR Modernization Framework** designed to transform traditional DTMF (keypad-only) telephony IVR systems into an AI-driven, speech-enabled conversational assistant for train enquiry and passenger support services.

---

## 🌐 Live Application & API

- 🚀 **Live Web Simulator**: [https://ivr-modern.vercel.app/](https://ivr-modern.vercel.app/)
- 🟢 **Backend Health Endpoint**: [https://ivr-modern.vercel.app/health](https://ivr-modern.vercel.app/health)
- 📊 **Flows API Endpoint**: [https://ivr-modern.vercel.app/api/flows](https://ivr-modern.vercel.app/api/flows)

---

## 🌟 Overview & Problem Solved

Traditional Interactive Voice Response (IVR) systems rely heavily on rigid touch-tone keypads (DTMF) and deep nested branching. Callers often struggle with long voice prompts, rigid navigation paths, and lack of flexibility.

This project **modernizes legacy IVR architectures** by introducing:
1. **Dual Interaction Model**: Seamlessly handles keypad (DTMF 0-9, *, #), direct text queries, and natural speech inputs.
2. **Intent Recognition & Gemini AI**: Uses Google Gemini AI (`google-genai` SDK) with pattern-matching fallback, fuzzy string distance scoring, and entity extraction to understand complex user queries.
3. **Dynamic State-Machine Engine**: JSON-driven flow transitions supporting over 10 distinct railway enquiry services with automatic state recovery and context collection.
4. **Interactive Single-Page Viewport Simulator**: Full-featured non-scrolling UI simulating call control, real-time timer, Web Speech API (STT & TTS), text input, call history, and downloadable JSON transcripts.

---

## ✨ Key Features

- 🎙️ **Speech & Voice Control**: Native Web Speech API integration for speech-to-text (STT) and text-to-speech (TTS) with speech interruption support.
- 💬 **Interactive Chat Input**: Text bar allowing users to type directly to the voice assistant alongside speech and keypad controls.
- 🔢 **Keypad (DTMF) Simulation**: Full phone keypad (0–9, *, #) with instant state transitions.
- 🧠 **Google Gemini AI Integration**: Recognizes user intent, extracts 5-digit train numbers, 10-digit PNRs, and travel classes.
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
- 📊 **Session & Call Logging**: In-memory session handling with persistent JSON call transcript generation (`backend/logs/` or `/tmp/logs`).
- 🧪 **100% Verified Test Suite**: Automated Pytest unit test coverage for FastAPI endpoints, health checks, and state transitions.

---

## 🚀 Deployment Guide (Vercel, Netlify & Docker)

### 🔹 Option 1: Full-Stack Deployment on Vercel (Live)
Both the FastAPI backend and HTML/JS frontend are deployed together on Vercel using `vercel.json` and `api/index.py`.

- **Live Site**: [https://ivr-modern.vercel.app/](https://ivr-modern.vercel.app/)
- **Vercel Build Stack**: `@vercel/python` (FastAPI Serverless API) + `@vercel/static` (Web UI).

---

### 🔹 Option 2: Frontend Deployment on Netlify
The repository includes a pre-configured `netlify.toml`.

1. Log in to [Netlify](https://app.netlify.com/).
2. Click **Add new site** → **Import an existing project** → Connect `praveen131106/ivr-modern`.
3. Set **Publish directory** to `frontend` and click **Deploy**.

---

### 🔹 Option 3: Backend API Container Deployment
Using Docker:
```bash
docker build -t ivr-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key" ivr-backend
```

---

## 🧪 Testing

Run all unit tests:
```bash
python -m pytest -v
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

======================== 10 passed in 0.20s ========================
```

---

## 📄 License

This project is open-source under the [MIT License](LICENSE.md).

## 👤 Author

**Praveen**
- GitHub: [@praveen131106](https://github.com/praveen131106)
- Repository: [ivr-modern](https://github.com/praveen131106/ivr-modern)
- Live Deployment: [https://ivr-modern.vercel.app/](https://ivr-modern.vercel.app/)
