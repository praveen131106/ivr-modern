/**
 * Train IVR System - Frontend JavaScript
 * Handles voice control, keypad input, and API integration
 */

const API_BASE_URL = "https://ivr-modern-backend1.onrender.com";


// Global state
let currentSessionId = null;
let callStartTime = null;
let callTimerInterval = null;
let recognition = null;
let isListening = false;
let callHistory = [];

// DOM elements
const startCallBtn = document.getElementById("startCall");
const endCallBtn = document.getElementById("endCall");
const micButton = document.getElementById("micButton");
const callTimer = document.getElementById("callTimer");
const callStatus = document.getElementById("callStatus");
const micStatus = document.getElementById("micStatus");
const ivrOutput = document.getElementById("ivrOutput");
const callHistoryDiv = document.getElementById("callHistory");
const clearHistoryBtn = document.getElementById("clearHistory");
const downloadTranscriptBtn = document.getElementById("downloadTranscript");
const keypadKeys = document.querySelectorAll(".key");

// Microphone permission state
let micPermissionGranted = false;
let micPermissionRequested = false;

// Initialize Web Speech API with persistent permission handling
function initSpeechRecognition() {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        console.warn("Speech recognition not supported");
        return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;  // Set to false - user controls when to listen
    recognition.interimResults = false;  // Only final results
    recognition.lang = "en-US";
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isListening = true;
        micStatus.textContent = "🎤 Listening...";
        micButton.classList.add("listening");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("Speech recognized:", transcript);
        
        // IMMEDIATELY stop speech when user speaks (interrupt welcome/messages)
        if ("speechSynthesis" in window && (isSpeaking || speechQueue.length > 0)) {
            window.speechSynthesis.cancel();
            isSpeaking = false;
            speechQueue = [];
            console.log("Speech interrupted by user input");
        }
        
        addToOutput(`You said: \