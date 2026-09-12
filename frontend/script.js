/**
 * Train IVR System - Frontend JavaScript Controller
 * Barge-in Speech Interruption, Hands-Free Voice Control (STT & TTS), Direct Typing & Gemini AI status.
 * Author: Praveen (Conversational IVR Modernization Framework)
 */

// Dynamic API URL determination (defaults to local backend if running locally)
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:";
const API_BASE_URL = window.IVR_API_URL || (isLocalhost ? "http://127.0.0.1:8000" : "");

// State variables
let currentSessionId = null;
let callStartTime = null;
let callTimerInterval = null;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let callHistory = [];
let lastSummary = null;
let micPermissionGranted = false;

// DOM Elements
const startCallBtn = document.getElementById("startCall");
const endCallBtn = document.getElementById("endCall");
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
const chatForm = document.getElementById("chatForm");
const userTextInput = document.getElementById("userTextInput");
const sendBtn = document.getElementById("sendBtn");
const micPermissionBanner = document.getElementById("micPermissionBanner");
const requestMicBtn = document.getElementById("requestMicBtn");

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

function showMicUnblockGuide() {
    if (!ivrOutput) return;

    if (micPermissionBanner) micPermissionBanner.classList.remove("hidden");

    const guideElement = document.createElement("div");
    guideElement.className = "banner-guide-card";
    guideElement.innerHTML = `
        <h4>🔒 How to Unblock Microphone Access in 2 Clicks:</h4>
        <ol>
            <li>Click the <strong>Tune / Lock icon (🔒)</strong> in your browser address bar (left of <code>127.0.0.1:8080</code>).</li>
            <li>Toggle <strong>Microphone</strong> to <strong>Allow</strong>.</li>
            <li>Refresh the page or click <strong>"Enable Mic Access"</strong> above.</li>
        </ol>
    `;
    ivrOutput.appendChild(guideElement);
    ivrOutput.scrollTop = ivrOutput.scrollHeight;
}

// Request Browser Microphone Access Dialog
async function requestMicPermission() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn("getUserMedia is not supported on this browser context.");
        return true;
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        micPermissionGranted = true;
        if (micPermissionBanner) micPermissionBanner.classList.add("hidden");
        if (micStatus) {
            micStatus.textContent = "🎤 Voice Active — Listening...";
            micStatus.classList.add("active");
        }
        return true;
    } catch (err) {
        console.warn("Microphone permission notice:", err);
        micPermissionGranted = false;
        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
            showMicUnblockGuide();
            if (micStatus) {
                micStatus.textContent = "⚠️ Mic Blocked in Browser Settings";
                micStatus.classList.remove("active");
            }
        }
        return false;
    }
}

let lastAssistantUtterance = "";

// Initialize Continuous Speech Recognition
function initSpeechRecognition() {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        console.warn("Speech recognition is not supported in this browser.");
        if (micStatus) micStatus.textContent = "🎤 Voice not supported";
        return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isListening = true;
        micPermissionGranted = true;
        if (micPermissionBanner) micPermissionBanner.classList.add("hidden");
        if (micStatus) {
            micStatus.textContent = "🎤 Voice Active — Listening...";
            micStatus.classList.add("active");
        }
    };

    recognition.onresult = async (event) => {
        const lastResultIndex = event.results.length - 1;
        const rawTranscript = event.results[lastResultIndex][0].transcript.trim();
        if (!rawTranscript) return;

        const transcriptLower = rawTranscript.toLowerCase();

        // 1. SELF-ECHO CHECK: Ignore input if mic hears assistant's own speaker output
        if (lastAssistantUtterance && lastAssistantUtterance.length > 5) {
            if (lastAssistantUtterance.includes(transcriptLower) || transcriptLower.includes(lastAssistantUtterance.slice(0, 15))) {
                console.log("Ignored self-echo of assistant speech:", rawTranscript);
                return;
            }
        }

        console.log("User Speech Recognized:", rawTranscript);

        // 2. BARGE-IN: Real user speech mid-sentence cancels assistant TTS voice
        if ("speechSynthesis" in window && isSpeaking) {
            console.log("Assistant voice interrupted by real user barge-in speech.");
            window.speechSynthesis.cancel();
            isSpeaking = false;
            lastAssistantUtterance = "";
        }

        if (userTextInput) userTextInput.value = rawTranscript;

        // Auto-start call session if not already active
        if (!currentSessionId) {
            await startCall();
        }

        addToOutput(rawTranscript, "user");
        sendInput(rawTranscript);
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition notice:", event.error);
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
            micPermissionGranted = false;
            showMicUnblockGuide();
            if (micStatus) {
                micStatus.textContent = "⚠️ Mic Blocked. Allow in URL bar.";
                micStatus.classList.remove("active");
            }
        }
    };

    recognition.onend = () => {
        isListening = false;
        // Auto-resume continuous listening whenever call is active & mic permission granted
        if (micPermissionGranted && currentSessionId) {
            setTimeout(() => startContinuousListening(), 200);
        } else {
            if (micStatus) {
                micStatus.textContent = micPermissionGranted ? "🎤 Voice Active — Listening..." : "Mic Inactive";
                if (!micPermissionGranted) micStatus.classList.remove("active");
            }
        }
    };

    return recognition;
}

function startContinuousListening() {
    if (!recognition) {
        recognition = initSpeechRecognition();
        if (!recognition) return;
    }

    if (!isListening) {
        try {
            recognition.start();
        } catch (e) {
            console.log("Mic start note:", e);
        }
    }
}

function stopContinuousListening() {
    if (recognition && isListening) {
        try {
            recognition.stop();
        } catch (e) {}
        isListening = false;
    }
}

// Speech Synthesis (Text-to-Speech)
function speakText(text) {
    if (!("speechSynthesis" in window)) return;
    
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }

    const cleanText = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}]/gu, '').trim();
    lastAssistantUtterance = cleanText.toLowerCase();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => { isSpeaking = true; };
    utterance.onend = () => {
        isSpeaking = false;
        setTimeout(() => { lastAssistantUtterance = ""; }, 600);
    };
    utterance.onerror = () => {
        isSpeaking = false;
        lastAssistantUtterance = "";
    };

    window.speechSynthesis.speak(utterance);
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

        const micOk = await requestMicPermission();

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

        // Enable UI Controls
        if (startCallBtn) startCallBtn.disabled = true;
        if (endCallBtn) endCallBtn.disabled = false;
        if (userTextInput) userTextInput.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        if (downloadTranscriptBtn) downloadTranscriptBtn.disabled = true;
        if (callStatus) callStatus.textContent = "In Call";
        if (statusDot) statusDot.classList.add("active");

        startTimer();
        addToOutput(data.message, "system");
        speakText(data.message);

        startContinuousListening();
    } catch (error) {
        console.error("Error starting call:", error);
        if (callStatus) callStatus.textContent = "Call Failed";
        alert(`Failed to start call. Ensure backend is running at ${API_BASE_URL}`);
    }
}

async function sendInput(inputVal) {
    if (!currentSessionId) {
        await startCall();
    }

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

    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }

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
        if (callStatus) callStatus.textContent = "Ready";
        if (statusDot) statusDot.classList.remove("active");
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

    if (userTextInput) userTextInput.disabled = false;
    if (sendBtn) sendBtn.disabled = false;

    requestMicPermission().then((ok) => {
        if (ok) startContinuousListening();
    });

    document.addEventListener("click", () => {
        if (!isListening && micPermissionGranted) {
            startContinuousListening();
        }
    }, { once: false });

    if (startCallBtn) startCallBtn.addEventListener("click", startCall);
    if (endCallBtn) endCallBtn.addEventListener("click", endCall);
    if (downloadTranscriptBtn) downloadTranscriptBtn.addEventListener("click", downloadTranscript);

    if (requestMicBtn) {
        requestMicBtn.addEventListener("click", async () => {
            const ok = await requestMicPermission();
            if (ok) {
                startContinuousListening();
            }
        });
    }

    // Chat Text Form Submission
    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = userTextInput ? userTextInput.value.trim() : "";
            if (text) {
                if ("speechSynthesis" in window && isSpeaking) {
                    window.speechSynthesis.cancel();
                    isSpeaking = false;
                }
                addToOutput(text, "user");
                await sendInput(text);
                userTextInput.value = "";
            }
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener("click", () => {
            callHistory = [];
            if (ivrOutput) {
                ivrOutput.innerHTML = `
                    <div class="welcome-card">
                        <h3>Welcome to IVR Voice Simulator</h3>
                        <p>Speak naturally, type in the chat bar below, or use the keypad!</p>
                    </div>`;
            }
        });
    }

    // Keypad Click Handlers
    keypadKeys.forEach((key) => {
        key.addEventListener("click", async () => {
            const keyValue = key.getAttribute("data-key");
            if (keyValue) {
                if ("speechSynthesis" in window && isSpeaking) {
                    window.speechSynthesis.cancel();
                    isSpeaking = false;
                }
                addToOutput(`Key pressed: ${keyValue}`, "user");
                await sendInput(keyValue);
            }
        });
    });

    // Sample Train Pills Handlers
    trainPills.forEach((pill) => {
        pill.addEventListener("click", async () => {
            const trainNum = pill.getAttribute("data-train");
            if (trainNum) {
                if ("speechSynthesis" in window && isSpeaking) {
                    window.speechSynthesis.cancel();
                    isSpeaking = false;
                }
                addToOutput(`Selected train ${trainNum}`, "user");
                await sendInput(trainNum);
            }
        });
    });

    // Suggestion Chips Handlers
    suggestionChips.forEach((chip) => {
        chip.addEventListener("click", async () => {
            const text = chip.getAttribute("data-input");
            if (text) {
                if ("speechSynthesis" in window && isSpeaking) {
                    window.speechSynthesis.cancel();
                    isSpeaking = false;
                }
                addToOutput(text, "user");
                await sendInput(text);
            }
        });
    });

    // Keyboard Listener
    document.addEventListener("keydown", async (e) => {
        if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;

        const allowedKeys = "0123456789*#";
        if (allowedKeys.includes(e.key)) {
            if ("speechSynthesis" in window && isSpeaking) {
                window.speechSynthesis.cancel();
                isSpeaking = false;
            }
            addToOutput(`Key pressed: ${e.key}`, "user");
            await sendInput(e.key);
        }
    });
});