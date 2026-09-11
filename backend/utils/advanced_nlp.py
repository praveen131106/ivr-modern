"""
Natural Language Processing Engine for Train IVR System
Implements intelligent intent recognition, fuzzy matching, entity extraction,
and optional Google Gemini AI integration.
"""

import os
import re
import json
from typing import Dict, Any, Tuple, Optional
from difflib import SequenceMatcher

# Optional Google Gemini AI integration
GEMINI_CLIENT = None
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        from google import genai
        GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
        print("Google Gemini AI SDK initialized successfully for IVR System.")
    except Exception as e:
        print(f"Gemini SDK initialization note: {e}")


class AdvancedNLP:
    """Advanced NLP engine with pattern matching, fuzzy logic, and Gemini AI integration"""
    
    def __init__(self):
        # Greeting patterns - handled separately for natural conversation
        self.greeting_patterns = {
            "greetings": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good night"],
            "responses": {
                "greeting": "Hello! I'm doing great, thank you for asking! How can I help you with your train enquiry today?",
                "how_are_you": "I'm doing wonderful, thank you! I'm here and ready to help you with all your train-related needs. What would you like to do today?",
                "thanks": "You're very welcome! Is there anything else I can help you with?",
                "polite": "That's very kind of you to ask! I'm here to assist you. How can I help with your train enquiry?"
            }
        }
        
        # Intent patterns with weighted importance
        self.intent_patterns = {
            "booking": {
                "keywords": ["book", "booking", "buy", "purchase", "reserve", "ticket", "tickets"],
                "weight": 1.0,
                "target": "flow:booking"
            },
            "status": {
                "keywords": ["status", "check", "running", "running status", "train status", "where is", "location"],
                "weight": 1.0,
                "target": "flow:status"
            },
            "schedule": {
                "keywords": ["schedule", "time", "timing", "departure", "arrival", "when", "what time"],
                "weight": 1.0,
                "target": "flow:schedule"
            },
            "cancellation": {
                "keywords": ["cancel", "cancellation", "cancel ticket", "refund", "delete booking"],
                "weight": 1.0,
                "target": "flow:cancellation"
            },
            "pnr": {
                "keywords": ["pnr", "pnr status", "check pnr", "booking status", "my ticket", "my booking"],
                "weight": 1.0,
                "target": "flow:pnr_status"
            },
            "seat_availability": {
                "keywords": ["seat", "seats", "available", "availability", "vacant", "empty seats", "booked"],
                "weight": 0.9,
                "target": "flow:seat_availability"
            },
            "fare": {
                "keywords": ["fare", "price", "cost", "how much", "charge", "fee", "ticket price"],
                "weight": 1.0,
                "target": "flow:fare_enquiry"
            },
            "trains_between": {
                "keywords": ["between", "from to", "trains between", "stations", "route", "find train"],
                "weight": 0.9,
                "target": "flow:train_between_stations"
            },
            "agent": {
                "keywords": ["agent", "support", "help", "representative", "human", "person", "talk to"],
                "weight": 1.0,
                "target": "flow:agent"
            },
            "repeat": {
                "keywords": ["repeat", "again", "say again", "repeat menu", "what are options"],
                "weight": 0.8,
                "target": "repeat_menu"
            },
            "menu": {
                "keywords": ["menu", "main menu", "options", "back", "go back", "home"],
                "weight": 0.8,
                "target": "main_menu"
            }
        }
        
        # Number words mapping
        self.number_words = {
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0",
            "first": "1", "second": "2", "third": "3"
        }
        
        # Class mappings
        self.class_mappings = {
            "sleeper": "Sleeper",
            "ac": "AC",
            "ac 3": "AC 3 Tier",
            "ac tier": "AC 3 Tier",
            "ac 2": "AC 2 Tier",
            "ac second": "AC 2 Tier",
            "first ac": "First AC",
            "first class": "First AC",
            "tatkal": "Tatkal"
        }
    
    def is_gemini_active(self) -> bool:
        """Check if Gemini AI client is active"""
        return GEMINI_CLIENT is not None

    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def is_greeting(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Check if input is a greeting and return appropriate response"""
        user_input_lower = user_input.lower().strip()
        
        greetings = self.greeting_patterns["greetings"]
        responses = self.greeting_patterns["responses"]
        
        for greeting in greetings:
            if greeting in user_input_lower:
                if "how are you" in user_input_lower or "how do you do" in user_input_lower:
                    return {"type": "greeting", "response": responses["how_are_you"]}
                else:
                    return {"type": "greeting", "response": responses["greeting"]}
        
        if any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
            return {"type": "greeting", "response": responses["thanks"]}
        
        if any(word in user_input_lower for word in ["nice", "good", "great", "wonderful"]):
            return {"type": "greeting", "response": responses["polite"]}
        
        return None

    def _call_gemini_nlp(self, user_input: str, current_state: str) -> Optional[Dict[str, Any]]:
        """Query Gemini AI model for intent & entity extraction"""
        if not GEMINI_CLIENT:
            return None
        try:
            prompt = f"""
            You are an AI intent classifier for a Train Enquiry IVR System.
            Classify user utterance: "{user_input}" (current state: {current_state}).
            Valid target options:
            - flow:booking (for booking/reserving tickets)
            - flow:status (for train running status)
            - flow:schedule (for train schedule/timings)
            - flow:cancellation (for cancelling tickets/refund)
            - flow:pnr_status (for PNR status)
            - flow:seat_availability (for seat availability)
            - flow:fare_enquiry (for ticket price/fare)
            - flow:train_between_stations (for trains between stations)
            - flow:agent (for human support)
            - repeat_menu (for repeating options)
            - main_menu (for returning to main menu)

            Return strictly a JSON object with keys:
            "target": string or null,
            "confidence": float between 0.0 and 1.0,
            "intent": string intent name or null.
            """
            response = GEMINI_CLIENT.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\n|\n```$", "", text, flags=re.MULTILINE)
            data = json.loads(text)
            if data.get("target"):
                data["engine"] = "gemini"
                return data
        except Exception as e:
            print(f"Gemini API note (falling back to local engine): {e}")
        return None
    
    def extract_intent(self, user_input: str, current_state: str = "main_menu") -> Optional[Dict[str, Any]]:
        """Extract intent using Gemini AI (if configured) or local pattern matcher"""
        user_input_lower = user_input.lower().strip()
        
        greeting_result = self.is_greeting(user_input_lower)
        if greeting_result:
            return greeting_result
        
        if len(user_input_lower) == 1 and user_input_lower in "0123456789*#":
            return None
        
        for word, num in self.number_words.items():
            if word in user_input_lower:
                return {"target": None, "keypad_value": num, "confidence": 1.0}

        # Attempt Gemini AI extraction first if active
        gemini_result = self._call_gemini_nlp(user_input, current_state)
        if gemini_result and gemini_result.get("confidence", 0) > 0.6:
            return gemini_result

        # Fallback to local pattern matcher
        best_match = None
        best_score = 0.0
        best_intent = None
        
        for intent_name, pattern_data in self.intent_patterns.items():
            keywords = pattern_data["keywords"]
            weight = pattern_data["weight"]
            
            for keyword in keywords:
                if keyword in user_input_lower:
                    # Longer matching keywords (e.g. "cancel ticket" vs "ticket") get higher precision score
                    length_bonus = min(len(keyword) * 0.02, 0.5)
                    score = (weight * 1.0) + length_bonus
                    if score > best_score:
                        best_score = score
                        best_match = pattern_data["target"]
                        best_intent = intent_name
                
                if len(keyword) > 4:
                    similarity = self.similarity(user_input_lower, keyword)
                    if similarity > 0.7:
                        score = weight * similarity
                        if score > best_score:
                            best_score = score
                            best_match = pattern_data["target"]
                            best_intent = intent_name
        
        if best_match and best_score > 0.6:
            return {
                "target": best_match,
                "confidence": min(best_score, 1.0),
                "intent": best_intent,
                "engine": "local"
            }
            
        # Infer booking flow if user mentions train number/name at main menu without explicit intent verb
        train_num = self.extract_train_number(user_input)
        if train_num and current_state == "main_menu":
            return {
                "target": "flow:booking",
                "confidence": 0.85,
                "intent": "booking",
                "engine": "local"
            }
        
        return None
    
    def extract_class_from_speech(self, user_input: str) -> Optional[str]:
        """Extract train class from speech"""
        if not user_input:
            return None
            
        user_input_lower = user_input.lower().strip()
        
        # If input is a train number or PNR digit sequence without class keywords, do not extract class
        if re.search(r'\b\d{4,10}\b', user_input_lower):
            if not any(c in user_input_lower for c in ["sleeper", "ac", "tatkal", "tier", "first class"]):
                return None

        for keyword, class_name in self.class_mappings.items():
            if keyword in user_input_lower:
                return class_name
        
        # Match standalone class choice numbers using word boundaries
        if re.search(r'\b(1|one|first)\b', user_input_lower):
            return "Sleeper"
        elif re.search(r'\b(2|two|second)\b', user_input_lower):
            return "AC"
        elif re.search(r'\b(3|three|third)\b', user_input_lower):
            return "Tatkal"
        
        return None
    
    def normalize_spoken_numbers(self, text: str) -> str:
        """Convert spoken number words ('one two seven one eight') and space-separated digit sequences ('1 2 7 1 8') into continuous digits ('12718')"""
        if not text:
            return ""
        words = text.lower().split()
        num_word_map = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "oh": "0"
        }
        normalized_words = [num_word_map.get(w, w) for w in words]
        normalized_text = " ".join(normalized_words)
        collapsed = re.sub(r'\b(?:\d\s+){3,9}\d\b', lambda m: m.group(0).replace(" ", ""), normalized_text)
        return collapsed

    def extract_train_number(self, user_input: str) -> Optional[str]:
        """Extract train number or mapped train name from natural speech input"""
        if not user_input:
            return None
            
        user_input = self.normalize_spoken_numbers(user_input)
        user_input_lower = user_input.lower().strip()
        
        # Exclude pure class names and keypad choices from being treated as train names
        if user_input_lower in ["ac", "sleeper", "tatkal", "ac 3 tier", "ac 2 tier", "first ac", "first class", "1", "2", "3", "4"]:
            return None
        
        # 1. Check for 5-digit or 4-6 digit train numbers
        numbers = re.findall(r'\b\d{5}\b', user_input)
        if numbers:
            return numbers[0]
            
        numbers = re.findall(r'\b\d{4,6}\b', user_input)
        if numbers:
            return numbers[0]
            
        # 2. Check for train names (Godavari, Secunderabad, Shatabdi, Rajdhani, Charminar, Duronto, Vande Bharat, etc.)
        train_name_map = {
            "godavari": "12718",
            "secunderabad": "17018",
            "shatabdi": "12009",
            "rajdhani": "12345",
            "charminar": "12760",
            "duronto": "12285",
            "garib rath": "12739",
            "vande bharat": "20701",
            "gautami": "12737",
            "falaknuma": "12703",
            "konark": "11019",
            "coromandel": "12841"
        }
        
        for name, num in train_name_map.items():
            if name in user_input_lower:
                return num
                
        # 3. Fallback: If user input mentions explicit train descriptors (e.g. "Visakha Express", "Chennai Mail")
        train_keywords = ["express", "superfast", "mail", "passenger", "local", "vande bharat", "shatabdi", "rajdhani"]
        if any(kw in user_input_lower for kw in train_keywords):
            cleaned_input = re.sub(r'\b(book|booking|ticket|tickets|for|a|an|the|check|status|in|class|on)\b', '', user_input_lower, flags=re.IGNORECASE).strip()
            if len(cleaned_input) >= 3:
                return cleaned_input.title()
            
        return None
    
    def extract_pnr(self, user_input: str) -> Optional[str]:
        """Extract PNR number from input"""
        if not user_input:
            return None
            
        user_input = self.normalize_spoken_numbers(user_input)
        numbers = re.findall(r'\b\d{10}\b', user_input)
        if numbers:
            return numbers[0]
        
        if "pnr" in user_input.lower():
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                return numbers[0]
        
        return None
    
    def understand_context(self, user_input: str, current_state: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        context = {
            "intent": None,
            "extracted_data": {},
            "suggested_action": None,
            "confidence": 0.0,
            "engine": "local"
        }
        
        intent_result = self.extract_intent(user_input, current_state)
        if intent_result:
            context["intent"] = intent_result.get("intent")
            context["suggested_action"] = intent_result.get("target")
            context["confidence"] = intent_result.get("confidence", 0.0)
            context["engine"] = intent_result.get("engine", "local")
        
        train_number = self.extract_train_number(user_input)
        if train_number:
            context["extracted_data"]["train_number"] = train_number
        
        pnr = self.extract_pnr(user_input)
        if pnr:
            context["extracted_data"]["pnr"] = pnr
        
        train_class = self.extract_class_from_speech(user_input)
        if train_class:
            context["extracted_data"]["train_class"] = train_class
        
        return context


# Global NLP instance
advanced_nlp = AdvancedNLP()
