# 🚂 Conversational IVR Modernization — Complete Technical & Conceptual Guide

> **Project Title**: Conversational IVR Modernization Framework for Railway Enquiry System  
> **Live Web App**: [https://ivr-modern.vercel.app/](https://ivr-modern.vercel.app/)  
> **GitHub Repository**: [praveen131106/ivr-modern](https://github.com/praveen131106/ivr-modern)  

---

## 📖 Table of Contents
1. [🎈 Explain Like I'm 5 (The Simple Analogy)](#1--explain-like-im-5-the-simple-analogy)
2. [⚙️ High-Level System Architecture](#2-️-high-level-system-architecture)
3. [🧠 Deep Technical Component Breakdown](#3--deep-technical-component-breakdown)
   - [A. Frontend Simulator & Web Speech API](#a-frontend-simulator--web-speech-api)
   - [B. FastAPI Backend & Session Handling](#b-fastapi-backend--session-handling)
   - [C. State Machine Engine (FlowManager)](#c-state-machine-engine-flowmanager)
   - [D. Advanced NLP & Gemini AI Engine](#d-advanced-nlp--gemini-ai-engine)
   - [E. Vercel Serverless Cloud Deployment](#e-vercel-serverless-cloud-deployment)
4. [🔁 Data Lifecycle Walkthrough (Step-by-Step Flow)](#4--data-lifecycle-walkthrough-step-by-step-flow)
5. [🎓 Master Interview Q&A (Technical Defense)](#5--master-interview-qa-technical-defense)

---

# 1. 🎈 Explain Like I'm 5 (The Simple Analogy)

Imagine you call a restaurant to order food:

- **Old IVR (The Rigid Robot)**: The robot voice says: *"Press 1 for Pizza, Press 2 for Burger, Press 3 for Drinks."* If you talk to it or say *"I want a pepperoni pizza,"* it gets confused and repeats the menu. You are forced to press keypad buttons.
- **Our Modern IVR (The Smart Assistant)**: You can press keypad buttons **OR** you can just talk naturally like a human: *"Hey, I want to book a ticket for Godavari Express tomorrow in Sleeper class."* 

Our system understands what you want, extracts details (like train numbers or travel class), guides you through booking, and speaks back to you in real-time.

---

# 2. ⚙️ High-Level System Architecture

```
                      ┌─────────────────────────────────────────┐
                      │    USER INTERFACE (Browser Viewport)    │
                      │  Keypad (DTMF) | Chat Bar | Voice (STT) │
                      └────────────────────┬────────────────────┘
                                           │
                                           │ HTTP POST /api/ivr/input
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │      FastAPI Backend (api/index.py)     │
                      │    Session Manager & Controller Router  │
                      └────────────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
     ┌────────────────────────────┐               ┌──────────────────────────────┐
     │   Advanced NLP Engine      │               │   JSON Finite State Machine  │
     │ (Gemini AI + Fuzzy Match)  │               │   (FlowManager Engine)       │
     └──────────────┬─────────────┘               └──────────────┬───────────────┘
                    │                                            │
                    └──────────────────────┬─────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │   Response Synthesizer & State Update   │
                      │ (JSON Payload -> Voice TTS + Chat UI)   │
                      └─────────────────────────────────────────┘
```

---

# 3. 🧠 Deep Technical Component Breakdown

### A. Frontend Simulator & Web Speech API
- **Files**: [`frontend/index.html`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/frontend/index.html), [`frontend/script.js`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/frontend/script.js), [`frontend/style.css`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/frontend/style.css)
- **Speech-to-Text (STT)**: Uses browser-native `webkitSpeechRecognition` / `SpeechRecognition` in continuous mode to capture spoken audio and transcribe it to text.
- **Text-to-Speech (TTS)**: Uses `SpeechSynthesisUtterance` to speak assistant responses back to the user at rate `0.95`.
- **Barge-in Interruption**: If the user speaks while the assistant is talking, `window.speechSynthesis.cancel()` immediately halts TTS output so the caller isn't talked over.
- **Self-Echo Suppression Filter**: Checks microphone input text against the last assistant utterance (`lastAssistantUtterance`) to ensure the mic doesn't re-read the computer's speakers.

---

### B. FastAPI Backend & Session Handling
- **Files**: [`backend/main.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/backend/main.py), [`api/index.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/api/index.py)
- **Framework**: Python 3.12 + FastAPI + Pydantic for fast asynchronous request validation.
- **Session Memory State**:
  - `sessions[session_id]` maintains in-memory state dictionary:
    ```python
    {
        "session_id": "uuid4-string",
        "started_at": "ISO-timestamp",
        "current_flow": "train_main",
        "current_state": "main_menu",
        "history": [ {"type": "user/system", "message": "...", "timestamp": "..."} ],
        "data": { "train_number": "12718", "class": "Sleeper", ... }
    }
    ```
- **Endpoints**:
  - `POST /api/ivr/start`: Initializes session, generates time-of-day greeting ("Good morning/afternoon"), and returns initial menu.
  - `POST /api/ivr/input`: Accepts user text/keypad digit, evaluates NLP/FSM state transitions, updates session data, and returns response payload.
  - `POST /api/ivr/end`: Closes session, calculates duration, and saves JSON transcript summary to `/tmp/logs` or `backend/logs/`.
  - `GET /health`: Returns server health status, uptime, active session count, and Gemini AI status.

---

### C. State Machine Engine (`FlowManager`)
- **Files**: [`backend/utils/flow_manager.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/backend/utils/flow_manager.py), [`backend/flows/*.json`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/backend/flows)
- **JSON State Graph Architecture**:
  - 10 modular JSON flow definitions: `train_main.json`, `booking.json`, `status.json`, `schedule.json`, `cancellation.json`, `pnr_status.json`, `seat_availability.json`, `fare_enquiry.json`, `train_between_stations.json`, `agent.json`.
- **State Transition Graph**:
  - States contain explicit keypad transition maps (`"1": "flow:booking"`, `"2": "flow:status"`), validation regexes, and prompt templates.
- **Subflow Hand-off**:
  - When `next_state` starts with `flow:<target_flow_name>`, `FlowManager` automatically switches `session["current_flow"]` to target JSON definition and initializes its entry state.

---

### D. Advanced NLP & Gemini AI Engine
- **File**: [`backend/utils/advanced_nlp.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/backend/utils/advanced_nlp.py)
- **Dual-Engine Architecture**:
  1. **Primary Engine (Google Gemini AI `gemini-2.5-flash`)**:
     - Invoked when `GEMINI_API_KEY` is present. Prompts LLM with valid flow targets to perform zero-shot intent recognition and structured JSON extraction.
  2. **Fallback Engine (Local Pattern Matcher & Fuzzy Scoring)**:
     - Invoked when Gemini API key is absent or network fails. Uses keyword weighting + `RapidFuzz` / `difflib.SequenceMatcher` similarity scoring (> 0.70 similarity threshold).
- **Entity Extractors**:
  - `normalize_spoken_numbers()`: Converts spoken word digits (*"one two seven one eight"*) or spaced numbers (*"1 2 7 1 8"*) into continuous digits (`"12718"`).
  - `extract_train_number()`: Regex pattern matching for 5-digit train numbers or name mapping (e.g. "Godavari" -> `12718`, "Shatabdi" -> `12009`).
  - `extract_pnr()`: Extracts 10-digit PNR sequences.
  - `extract_class_from_speech()`: Extracts travel classes (`Sleeper`, `AC`, `Tatkal`).

---

### E. Vercel Serverless Cloud Deployment
- **Files**: [`vercel.json`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/vercel.json), [`api/index.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/api/index.py)
- **Serverless Architecture**:
  - `@vercel/python` turns `api/index.py` into an AWS Lambda / Vercel Serverless Function.
  - `@vercel/static` hosts `frontend/` files.
- **Single Domain Same-Origin Routing**:
  - Requests to `/api/*` and `/health` route directly to Python serverless functions on the same domain (`https://ivr-modern.vercel.app`), completely eliminating CORS configuration overhead.

---

# 4. 🔁 Data Lifecycle Walkthrough (Step-by-Step Flow)

Let's trace what happens when a caller says: **"Book a ticket for Godavari Express"**:

```
1. USER SPEAKS: "Book a ticket for Godavari Express"
   ↓
2. STT ENCODING: Web Speech API converts audio -> text string "Book a ticket for Godavari Express"
   ↓
3. HTTP REQUEST: JS controller sends POST to /api/ivr/input { "session_id": "abc-123", "input": "Book a ticket for Godavari Express" }
   ↓
4. INTENT EXTRACTION: AdvancedNLP receives string:
   - Identifies intent "booking" (via Gemini AI or local keyword matcher) -> Target state "flow:booking"
   - Extracts train entity -> train_number "12718" (Godavari Express)
   ↓
5. STATE TRANSITION: FlowManager executes:
   - Transitions current_flow from "train_main" -> "booking.json"
   - Stores train_number "12718" in session["data"]
   - Moves to state "select_class"
   ↓
6. RESPONSE SYNTHESIS: Backend returns JSON:
   {
     "session_id": "abc-123",
     "message": "Selected Godavari Express (12718). Which class would you like? Press 1 for Sleeper, Press 2 for AC, Press 3 for Tatkal.",
     "state": "select_class"
   }
   ↓
7. AUDIO OUTPUT & UI: JS receives response -> Displays text in chat stream -> Triggers SpeechSynthesis TTS voice output.
```

---

# 5. 🎓 Master Interview Q&A (Technical Defense)

### Q1: What problem does this project solve?
> **Answer**: Legacy IVR systems rely on rigid DTMF keypad trees that cause long call durations and high user frustration. Our modernization framework introduces a dual interaction model combining DTMF keypad, text chat, and natural voice speech with AI intent classification and dynamic state machine navigation.

### Q2: How do you handle state management across conversational turns?
> **Answer**: We built an in-memory session manager in FastAPI. Each call gets a unique UUID `session_id` mapping to a state context containing the active JSON flow (`current_flow`), node (`current_state`), slots (`data`), and exchange history (`history`).

### Q3: What happens if the Gemini AI API fails or is offline?
> **Answer**: We built a hybrid failover mechanism in [`backend/utils/advanced_nlp.py`](file:///c:/Users/shiruken/Downloads/infosys%20intern/ivr-modern-main/backend/utils/advanced_nlp.py). If the Gemini API key is missing or fails due to network latency, the system automatically falls back to our local NLP engine using keyword weighting and RapidFuzz string distance matching without interrupting the user session.

### Q4: How does the voice system handle "Barge-in" (user interrupting the assistant mid-sentence)?
> **Answer**: In `script.js`, when Web Speech API detects new user speech while `isSpeaking` is true, it immediately calls `window.speechSynthesis.cancel()`. This stops assistant audio instantly so the caller isn't talked over.

### Q5: How do you prevent the microphone from hearing its own speaker output (Self-Echo)?
> **Answer**: We store the assistant's outgoing prompt in `lastAssistantUtterance`. When the Web Speech API returns recognized audio text, we filter it against `lastAssistantUtterance` to ignore self-echoes.

### Q6: How is the application deployed on Vercel?
> **Answer**: We configured `vercel.json` with `@vercel/python` for backend API routing (`api/index.py`) and `@vercel/static` for static frontend assets (`frontend/`). Both run under a unified domain (`ivr-modern.vercel.app`), enabling same-origin API requests without CORS issues.

### Q7: How do you normalize spoken train numbers like "one two seven one eight"?
> **Answer**: In `normalize_spoken_numbers()`, we map English number words (`one` -> `1`, `two` -> `2`) and use regex substitution (`re.sub`) to collapse space-separated digit sequences (`"1 2 7 1 8"`) into continuous strings (`"12718"`).

### Q8: How are tests structured in this repository?
> **Answer**: We maintain 10 unit tests across `test_api.py`, `test_api_endpoints.py`, and `test_flow_manager.py` using `pytest` and `httpx.AsyncClient` to test FastAPI endpoint lifecycle, session isolation, and state machine transitions.

---

### 🌟 One-Sentence Resume Pitch
> **"Built and deployed a production-ready Conversational IVR Modernization platform featuring FastAPI serverless architecture, Web Speech STT/TTS voice controls, Google Gemini AI zero-shot intent recognition with local fuzzy NLP fallback, and dynamic JSON state machines."**
