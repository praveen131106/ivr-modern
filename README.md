# 🚂 Conversational IVR Modernization - Train Enquiry System

A comprehensive, production-ready **Conversational IVR Modernization Framework** for a Train Enquiry System. This project implements all three milestones of IVR modernization with advanced voice control, keypad input, intelligent NLP-based menu understanding, and dynamic conversational responses.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [System Architecture](#system-architecture)
- [Milestones Implementation](#milestones-implementation)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project modernizes traditional IVR systems by implementing a conversational interface that supports both voice and keypad interactions. The system uses natural language processing to understand user intent, provides dynamic responses based on context, and offers a seamless user experience for train-related enquiries.

### Key Capabilities

- **Dual Input Methods**: Voice commands and keypad navigation
- **Intelligent NLP**: Pattern-based intent recognition with fuzzy matching
- **Dynamic Conversations**: Context-aware responses with automatic flow progression
- **Real-time Speech**: Text-to-speech and speech-to-text integration
- **Session Management**: Complete call tracking and transcript generation

## ✨ Features

### Core Features
- ✅ **Voice Control** - Full Web Speech API integration for speech-to-text and text-to-speech
- ✅ **Keypad Input** - All keys (0-9, *, #) mapped to distinct functions
- ✅ **Intelligent NLP** - Pattern-based natural language understanding with fuzzy matching
- ✅ **Dynamic Responses** - Real-time train status, booking confirmations, schedules
- ✅ **Session Management** - In-memory session handling with call logging
- ✅ **Call History** - Transcript download and localStorage persistence
- ✅ **Modern UI** - Beautiful, responsive IVR simulator interface
- ✅ **100% Local** - No external APIs or cloud services required

### Advanced Features
- **Intent Recognition** - Understands variations in user input
- **Entity Extraction** - Automatically extracts train numbers, PNR, classes from speech
- **Greeting Handling** - Natural conversation flow with greeting responses
- **Error Recovery** - Graceful handling of invalid inputs with helpful suggestions
- **Speech Interruption** - User can interrupt system prompts at any time
- **Multi-flow Support** - 10+ distinct service flows (Booking, Status, PNR, etc.)

## 📂 Project Structure

```
train-ivr-system/
│
├── backend/
│   ├── main.py                      # FastAPI application entry point
│   ├── flows/                       # JSON-based flow definitions
│   │   ├── train_main.json         # Main menu flow
│   │   ├── booking.json            # Ticket booking flow
│   │   ├── status.json             # Train status check flow
│   │   ├── schedule.json           # Schedule enquiry flow
│   │   ├── cancellation.json       # Ticket cancellation flow
│   │   ├── pnr_status.json         # PNR status check flow
│   │   ├── seat_availability.json  # Seat availability flow
│   │   ├── fare_enquiry.json       # Fare enquiry flow
│   │   ├── train_between_stations.json  # Route finder flow
│   │   └── agent.json              # Customer support flow
│   ├── utils/
│   │   ├── flow_manager.py         # Flow navigation and state management
│   │   └── advanced_nlp.py         # NLP engine for intent recognition
│   └── logs/                        # Call logs (auto-created)
│
├── frontend/
│   ├── index.html                  # IVR simulator interface
│   ├── script.js                   # Voice control & API integration
│   └── style.css                   # Modern, responsive styling
│
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git ignore rules
├── start_backend.bat               # Windows startup script
├── start_backend.sh                # Linux/Mac startup script
└── README.md                        # This file
```

## 🚀 Installation

### Prerequisites

- **Python** 3.9 or higher
- **Modern Web Browser** (Chrome, Edge, or Firefox) with Web Speech API support
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/praveen131106/AI-conv-train-ivr.git
   cd AI-conv-train-ivr
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create logs directory (optional):**
   ```bash
   mkdir -p backend/logs
   ```

## 💻 Usage

### Starting the Backend Server

**Option 1: Using the startup script (Windows)**
```bash
start_backend.bat
```

**Option 2: Using the startup script (Linux/Mac)**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Option 3: Manual start**
```bash
cd backend
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### Running the Frontend

1. **Direct file access:**
   - Navigate to `frontend/index.html`
   - Open in a modern web browser (Chrome/Edge recommended)

2. **Using a local web server (recommended):**
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then open `http://localhost:8080` in your browser

### Using the IVR System

1. **Start a Call**
   - Click "📞 Start Call" button
   - System will greet you and present menu options

2. **Interact via Keypad**
   - Click any keypad button (0-9, *, #)
   - Or use keyboard keys (1-9, 0, *, #)
   - Each key has a unique function

3. **Use Voice Control**
   - Click "🎤 Speak" button
   - Allow microphone permissions when prompted
   - Speak naturally: "Book a ticket", "Check train status", etc.
   - System understands and responds

4. **Menu Options**
   - **Press 1** or say "book" → Book a train ticket
   - **Press 2** or say "status" → Check train status
   - **Press 3** or say "schedule" → Get train schedule
   - **Press 4** or say "cancel" → Cancel a ticket
   - **Press 5** or say "PNR" → Check PNR status
   - **Press 6** or say "seat" → Check seat availability
   - **Press 7** or say "fare" → Fare enquiry
   - **Press 8** or say "between stations" → Find trains between stations
   - **Press 0** or say "repeat" → Repeat menu
   - **Press 9** or say "agent" → Connect to support

5. **End Call**
   - Click "📴 End Call"
   - Download transcript if needed

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /`
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Train IVR System API",
  "version": "1.0.0",
  "endpoints": {
    "/api/ivr/start": "Start new IVR session",
    "/api/ivr/input": "Process user input",
    "/api/ivr/end": "End IVR session",
    "/api/flows": "Get available flows"
  }
}
```

#### `POST /api/ivr/start`
Initialize a new IVR session.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Welcome message with menu options...",
  "state": "main_menu",
  "options": {
    "1": "Book Train Ticket",
    "2": "Check Train Status",
    ...
  },
  "is_end": false
}
```

#### `POST /api/ivr/input`
Process user input (keypad or voice).

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "input": "1" or "book a ticket"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "System response...",
  "state": "next_state",
  "options": {...},
  "is_end": false
}
```

#### `POST /api/ivr/end`
End an IVR session and retrieve call summary.

**Request Body:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "message": "Call ended successfully",
  "summary": {
    "session_id": "...",
    "duration_seconds": 45.2,
    "started_at": "2025-01-02T...",
    "ended_at": "2025-01-02T...",
    "total_exchanges": 5,
    "transcript": [...],
    "collected_data": {...}
  }
}
```

#### `GET /api/flows`
Get list of available flows and their structure.

#### `GET /api/session/{session_id}`
Get detailed session information (for debugging).

## 🏗️ System Architecture

### Backend Architecture

**FastAPI Application (`main.py`)**
- RESTful API with CORS support
- Session management with UUID-based identifiers
- Request/response validation using Pydantic
- Error handling and logging

**Flow Management System (`utils/flow_manager.py`)**
- JSON-based flow definitions
- State machine implementation
- Dynamic flow transitions
- Data collection and validation
- Response generation

**NLP Engine (`utils/advanced_nlp.py`)**
- Intent recognition using pattern matching
- Fuzzy string matching for typos
- Entity extraction (train numbers, PNR, classes)
- Greeting detection and handling
- Confidence scoring

### Frontend Architecture

**HTML Interface (`index.html`)**
- Modern, responsive design
- Keypad simulation
- Real-time call display
- History management

**JavaScript Logic (`script.js`)**
- Web Speech API integration
- Speech-to-text and text-to-speech
- API communication with Fetch API
- Session management
- Local storage for call history

**Styling (`style.css`)**
- Gradient-based modern design
- Responsive layout
- Smooth animations
- Accessible color schemes

## 📊 Milestones Implementation

### Milestone 1: Legacy System Analysis & Flow Definition

**Objectives:**
- Analyze existing IVR structure
- Define complete flow hierarchy
- Create structured flow definitions

**Implementation:**
- ✅ 10 JSON flow files for all service options
- ✅ Hierarchical state management
- ✅ Dynamic flow loading system
- ✅ Complete menu structure with 12 options

**Files:**
- `backend/flows/train_main.json` - Main menu
- `backend/flows/*.json` - Individual service flows

### Milestone 2: Integration Layer (Backend API)

**Objectives:**
- Create RESTful API for IVR operations
- Implement session management
- Process multiple input types

**Implementation:**
- ✅ FastAPI backend with 5+ endpoints
- ✅ UUID-based session tracking
- ✅ Dual input processing (keypad + voice)
- ✅ Flow transition engine
- ✅ Dynamic response generation
- ✅ Call logging system

**Files:**
- `backend/main.py` - API implementation
- `backend/utils/flow_manager.py` - Flow processing

### Milestone 3: Conversational Interface (Frontend)

**Objectives:**
- Enhance IVR simulator with voice capabilities
- Integrate with backend API
- Provide natural user experience

**Implementation:**
- ✅ Voice recognition (Web Speech API)
- ✅ Text-to-speech synthesis
- ✅ Real-time conversation display
- ✅ Call history and transcripts
- ✅ Speech interruption handling
- ✅ Microphone permission management

**Files:**
- `frontend/index.html` - Interface
- `frontend/script.js` - Voice integration
- `frontend/style.css` - Styling

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Programming language
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **JSON** - Flow configuration

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript (ES6+)** - Logic
- **Web Speech API** - Voice features
- **Fetch API** - HTTP requests
- **LocalStorage** - Data persistence

### NLP
- **Pattern Matching** - Intent recognition
- **Sequence Matcher** - Fuzzy matching
- **Regular Expressions** - Entity extraction
- **Rule-based System** - Context understanding

## ⚙️ Configuration

### Backend Configuration

**Change API Port:**
Edit `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port number
```

**Modify Flow Definitions:**
Edit JSON files in `backend/flows/`:
- Add/modify states
- Update transitions
- Change messages
- Add new speech patterns

### Frontend Configuration

**Change API URL:**
Edit `frontend/script.js`:
```javascript
const API_BASE_URL = "http://localhost:8000"; // Update if needed
```

**Adjust Speech Settings:**
Edit `frontend/script.js`:
```javascript
utterance.rate = 0.92;  // Speech rate (0.1 - 10)
utterance.pitch = 1.0;  // Speech pitch (0 - 2)
utterance.volume = 1;   // Speech volume (0 - 1)
```

## 🐛 Troubleshooting

### Backend Issues

**Server won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check port availability
netstat -an | findstr :8000  # Windows
lsof -i :8000                # Linux/Mac
```

**Flows not loading:**
- Verify JSON files exist in `backend/flows/`
- Check JSON syntax is valid
- Review backend console for error messages

### Frontend Issues

**Voice recognition not working:**
- Use Chrome or Edge browser
- Allow microphone permissions
- Check browser console (F12) for errors
- Verify HTTPS/localhost (required for microphone)

**API connection errors:**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings
- Verify firewall isn't blocking port 8000
- Review browser console for detailed errors

**Speech synthesis not working:**
- Check browser supports Web Speech API
- Verify voices are loaded (check console)
- Try different browser if issues persist

## 📝 Development Notes

### Code Organization

- **Separation of Concerns**: Backend handles logic, frontend handles UI
- **Modular Design**: Flow definitions separate from processing logic
- **Extensible**: Easy to add new flows or modify existing ones

### Best Practices Implemented

- Error handling at all levels
- Graceful degradation for unsupported features
- User-friendly error messages
- Session state management
- Clean code structure

### Future Enhancements

Potential improvements for production:
- Database integration for session persistence
- Redis for distributed session management
- WebSocket for real-time bidirectional communication
- Authentication and authorization
- Rate limiting and security measures
- HTTPS for secure voice data transmission
- Machine learning for improved NLP
- Multi-language support

## 📄 License

This project is developed for educational and demonstration purposes as part of an IVR modernization initiative.

## 👥 Author

**Praveen**
- GitHub: [praveen131106](https://github.com/praveen131106)
- Repository: [AI-conv-train-ivr](https://github.com/praveen131106/AI-conv-train-ivr)

## 🙏 Acknowledgments

- FastAPI framework for excellent backend infrastructure
- Web Speech API team for voice capabilities
- Modern web standards community
- Open source contributors

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 2025
