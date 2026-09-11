/**
 * Train IVR System - Frontend JavaScript Controller
 * Handles voice control (STT & TTS), keypad input, API interaction, and Gemini AI status.
 * Author: Praveen (Conversational IVR Modernization Framework)
 */

// Dynamic API URL determination (defaults to local backend if running locally)
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:";
const API_BASE_URL = window.IVR_API_URL || (isLocalhost ? "http://127.0.0.1:8000" : "https://ivr-modern-backend1.onrender.com");

// State variables
let currentSessionId = null;
let callStartTime = null;
let callTimerInterval = null;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let callHistory = [];
let lastSummary = null;

// DOM Elements
const startCallBtn = document.getElementById("startCall");
const endCallBtn = document.getElementById("endCall");
const micButton = document.getElementById("micButton");
const callTimer = document.getElementById("callTimer");
const callStatus = document.getElementById("callStatus");
const statusDot = document.getElementById("statusDot");
const micStatus = document.getElementById("micStatus");
const ivrOutput = document.getElementById("ivrOutput");
const clearHistoryBtn = document.getElementById("clearHistory");
const downloadTranscriptBtn = document.getElementById("downloadTranscript");
const keypadKeys = document.querySelectorAll(".key");
const trainPills = document.querySelectorAll(".train-pill");
const suggestionChips = document.querySelectorAll(".chip");
const engineText = document.getElementById("engineText");

// Check Backend Engine Status on Load
async function checkEngineHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            if (engineText) {
                engineText.textContent = data.gemini_active ? "Engine: Gemini AI ✨" : "Engine: Local NLP ⚡";
            }
        }
    } catch (e) {
        console.log("Health check note:", e);
    }
}

// Initialize Speech Recognition
function initSpeechRecognition() {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        console.warn("Speech recognition is not supported in this browser.");
        if (micStatus) micStatus.textContent = "🎤 Voice not supported";
        return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isListening = true;
        if (micStatus) micStatus.textContent = "🎤 Listening... Speak now!";
        if (micButton) micButton.classList.add("listening");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("Speech recognized:", transcript);
        addToOutput(transcript, "user");
        sendInput(transcript);
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition notice:", event.error);
        if (event.error === "no-speech") {
            if (micStatus) micStatus.textContent = "No speech heard. Try again.";
        } else if (event.error !== "aborted") {
            if (micStatus) micStatus.textContent = `Mic error: ${event.error}`;
        }
        stopListening();
    };

    recognition.onend = () => {
        stopListening();
    };

    return recognition;
}

function stopListening() {
    isListening = false;
    if (micStatus) micStatus.textContent = currentSessionId ? "Call Active" : "Mic Inactive";
    if (micButton) micButton.classList.remove("listening");
}

function toggleMic() {
    if (!currentSessionId) {
        alert("Please start a call first.");
        return;
    }

    // Stop any ongoing Text-To-Speech to free up the audio device
    stopSpeechSynthesis();

    if (!recognition) {
        recognition = initSpeechRecognition();
        if (!recognition) {
            alert("Speech recognition is not supported on your browser. Please use Google Chrome or Microsoft Edge.");
            return;
        }
    }

    if (isListening) {
        try { recognition.stop(); } catch (e) {}
        stopListening();
    } else {
        // Small 200ms timeout ensures audio channel is clear before microphone start
        setTimeout(() => {
            try {
                recognition.start();
            } catch (e) {
                console.error("Failed to start mic:", e);
                stopListening();
            }
        }, 200);
    }
}

// Speech Synthesis (Text-to-Speech)
function speakText(text) {
    if (!("speechSynthesis" in window)) return;
    
    stopSpeechSynthesis();
    const cleanText = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}]/gu, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => { isSpeaking = true; };
    utterance.onend = () => { isSpeaking = false; };
    utterance.onerror = () => { isSpeaking = false; };

    window.speechSynthesis.speak(utterance);
}

function stopSpeechSynthesis() {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
    }
}

// Timer Functions
function startTimer() {
    callStartTime = Date.now();
    callTimerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, "0");
        const secs = String(elapsed % 60).padStart(2, "0");
        if (callTimer) callTimer.textContent = `${mins}:${secs}`;
    }, 1000);
}

function stopTimer() {
    if (callTimerInterval) {
        clearInterval(callTimerInterval);
        callTimerInterval = null;
    }
    if (callTimer) callTimer.textContent = "00:00";
}

// Output and Chat Stream Display
function addToOutput(message, type = "system") {
    if (!ivrOutput) return;

    // Remove welcome card on first message
    const welcomeCard = ivrOutput.querySelector(".welcome-card");
    if (welcomeCard) welcomeCard.remove();

    const msgElement = document.createElement("div");
    msgElement.className = `chat-msg ${type === "user" ? "user-msg" : "system-msg"}`;
    msgElement.textContent = message;
    ivrOutput.appendChild(msgElement);
    ivrOutput.scrollTop = ivrOutput.scrollHeight;

    callHistory.push({
        type: type,
        message: message,
        timestamp: new Date().toLocaleTimeString()
    });
}

// API Communication
async function startCall() {
    try {
        if (callStatus) callStatus.textContent = "Connecting...";
        const response = await fetch(`${API_BASE_URL}/api/ivr/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        currentSessionId = data.session_id;
        callHistory = [];
        lastSummary = null;
        if (ivrOutput) ivrOutput.innerHTML = "";

        // UI Updates
        if (startCallBtn) startCallBtn.disabled = true;
        if (endCallBtn) endCallBtn.disabled = false;
        if (micButton) micButton.disabled = false;
        if (downloadTranscriptBtn) downloadTranscriptBtn.disabled = true;
        if (callStatus) callStatus.textContent = "In Call";
        if (statusDot) statusDot.classList.add("active");
        if (micStatus) micStatus.textContent = "Call Active";

        startTimer();
        addToOutput(data.message, "system");
        speakText(data.message);
    } catch (error) {
        console.error("Error starting call:", error);
        if (callStatus) callStatus.textContent = "Call Failed";
        alert(`Failed to start call. Ensure backend is running at ${API_BASE_URL}`);
    }
}

async function sendInput(inputVal) {
    if (!currentSessionId) return;

    stopSpeechSynthesis();
    try {
        const response = await fetch(`${API_BASE_URL}/api/ivr/input`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSessionId,
                input: String(inputVal)
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        addToOutput(data.message, "system");
        speakText(data.message);

        if (data.is_end) {
            setTimeout(() => endCall(), 4000);
        }
    } catch (error) {
        console.error("Error sending input:", error);
        addToOutput("Failed to connect to IVR backend. Please try again.", "system");
    }
}

async function endCall() {
    if (!currentSessionId) return;

    stopSpeechSynthesis();
    stopListening();

    try {
        const response = await fetch(`${API_BASE_URL}/api/ivr/end`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId })
        });

        if (response.ok) {
            const data = await response.json();
            lastSummary = data.summary;
            addToOutput("Call ended. Thank you for calling Train Enquiry System.", "system");
            if (downloadTranscriptBtn) downloadTranscriptBtn.disabled = false;
        }
    } catch (error) {
        console.error("Error ending call:", error);
    } finally {
        currentSessionId = null;
        stopTimer();

        if (startCallBtn) startCallBtn.disabled = false;
        if (endCallBtn) endCallBtn.disabled = true;
        if (micButton) micButton.disabled = true;
        if (callStatus) callStatus.textContent = "Ready";
        if (statusDot) statusDot.classList.remove("active");
        if (micStatus) micStatus.textContent = "Mic Inactive";
    }
}

// Download Call Transcript
function downloadTranscript() {
    const transcriptData = lastSummary || {
        session_id: currentSessionId || "local_session",
        exported_at: new Date().toISOString(),
        transcript: callHistory
    };

    const blob = new Blob([JSON.stringify(transcriptData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ivr_transcript_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Event Listeners Setup
document.addEventListener("DOMContentLoaded", () => {
    checkEngineHealth();
    initSpeechRecognition();

    if (startCallBtn) startCallBtn.addEventListener("click", startCall);
    if (endCallBtn) endCallBtn.addEventListener("click", endCall);
    if (micButton) micButton.addEventListener("click", toggleMic);
    if (downloadTranscriptBtn) downloadTranscriptBtn.addEventListener("click", downloadTranscript);

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener("click", () => {
            callHistory = [];
            if (ivrOutput) {
                ivrOutput.innerHTML = `
                    <div class="welcome-card">
                        <h3>Welcome to IVR Voice Simulator</h3>
                        <p>Click <strong>"Start Call"</strong> to begin. Speak naturally or use the keypad to navigate train enquiries.</p>
                    </div>`;
            }
        });
    }

    // Keypad Click Handlers
    keypadKeys.forEach((key) => {
        key.addEventListener("click", () => {
            const keyValue = key.getAttribute("data-key");
            if (keyValue && currentSessionId) {
                addToOutput(`Key pressed: ${keyValue}`, "user");
                sendInput(keyValue);
            }
        });
    });

    // Sample Train Pills Handlers
    trainPills.forEach((pill) => {
        pill.addEventListener("click", () => {
            const trainNum = pill.getAttribute("data-train");
            if (trainNum && currentSessionId) {
                addToOutput(`Selected train ${trainNum}`, "user");
                sendInput(trainNum);
            }
        });
    });

    // Suggestion Chips Handlers
    suggestionChips.forEach((chip) => {
        chip.addEventListener("click", () => {
            const text = chip.getAttribute("data-input");
            if (text && currentSessionId) {
                addToOutput(text, "user");
                sendInput(text);
            }
        });
    });

    // Keyboard Listener
    document.addEventListener("keydown", (e) => {
        if (!currentSessionId) return;
        if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;

        const allowedKeys = "0123456789*#";
        if (allowedKeys.includes(e.key)) {
            addToOutput(`Key pressed: ${e.key}`, "user");
            sendInput(e.key);
        }
    });
});