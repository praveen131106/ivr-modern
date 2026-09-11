"""
Natural Language Processing Engine for Train IVR System
Implements intelligent intent recognition, fuzzy matching, and context understanding
using pattern-based algorithms and sequence matching techniques.
"""

import re
from typing import Dict, Any, Tuple, Optional
from difflib import SequenceMatcher


class AdvancedNLP:
    """Advanced NLP engine with intent recognition and fuzzy matching"""
    
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
    
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def is_greeting(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Check if input is a greeting and return appropriate response"""
        user_input_lower = user_input.lower().strip()
        
        greetings = self.greeting_patterns["greetings"]
        responses = self.greeting_patterns["responses"]
        
        # Check for greetings
        for greeting in greetings:
            if greeting in user_input_lower:
                if "how are you" in user_input_lower or "how do you do" in user_input_lower:
                    return {"type": "greeting", "response": responses["how_are_you"]}
                else:
                    return {"type": "greeting", "response": responses["greeting"]}
        
        # Check for thanks
        if any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
            return {"type": "greeting", "response": responses["thanks"]}
        
        # Check for polite questions
        if any(word in user_input_lower for word in ["nice", "good", "great", "wonderful"]):
            return {"type": "greeting", "response": responses["polite"]}
        
        return None
    
    def extract_intent(self, user_input: str, current_state: str = "main_menu") -> Optional[Dict[str, Any]]:
        """
        Advanced intent extraction with fuzzy matching
        
        Returns: {"target": "flow:booking", "confidence": 0.95, "intent": "booking"}
        """
        user_input_lower = user_input.lower().strip()
        
        # Check for greetings first
        greeting_result = self.is_greeting(user_input_lower)
        if greeting_result:
            return greeting_result
        
        # Check for exact number matches first
        if len(user_input_lower) == 1 and user_input_lower in "0123456789*#":
            return None  # Let keypad handler deal with it
        
        # Check for number words
        for word, num in self.number_words.items():
            if word in user_input_lower:
                # Return as keypad input
                return {"target": None, "keypad_value": num, "confidence": 1.0}
        
        best_match = None
        best_score = 0.0
        best_intent = None
        
        # Score each intent pattern
        for intent_name, pattern_data in self.intent_patterns.items():
            keywords = pattern_data["keywords"]
            weight = pattern_data["weight"]
            
            # Check exact keyword matches
            for keyword in keywords:
                if keyword in user_input_lower:
                    score = weight * 1.0
                    if score > best_score:
                        best_score = score
                        best_match = pattern_data["target"]
                        best_intent = intent_name
                
                # Check fuzzy matching for longer keywords
                if len(keyword) > 4:
                    similarity = self.similarity(user_input_lower, keyword)
                    if similarity > 0.7:
                        score = weight * similarity
                        if score > best_score:
                            best_score = score
                            best_match = pattern_data["target"]
                            best_intent = intent_name
        
        # Check for multi-word patterns
        for intent_name, pattern_data in self.intent_patterns.items():
            # Look for compound patterns like "book ticket", "check status"
            keywords = pattern_data["keywords"]
            for keyword in keywords:
                # Extract surrounding context
                if keyword in user_input_lower:
                    context_words = user_input_lower.split()
                    keyword_index = context_words.index(keyword) if keyword in context_words else -1
                    
                    if keyword_index >= 0:
                        # Check nearby words for context
                        nearby = " ".join(context_words[max(0, keyword_index-2):keyword_index+3])
                        enhanced_score = pattern_data["weight"] * 1.2
                        
                        if enhanced_score > best_score:
                            best_score = enhanced_score
                            best_match = pattern_data["target"]
                            best_intent = intent_name
        
        if best_match and best_score > 0.6:
            return {
                "target": best_match,
                "confidence": min(best_score, 1.0),
                "intent": best_intent
            }
        
        return None
    
    def extract_class_from_speech(self, user_input: str) -> Optional[str]:
        """Extract train class from speech"""
        user_input_lower = user_input.lower()
        
        for keyword, class_name in self.class_mappings.items():
            if keyword in user_input_lower:
                return class_name
        
        # Check for numbers
        if "1" in user_input or "one" in user_input or "first" in user_input:
            return "Sleeper"
        elif "2" in user_input or "two" in user_input or "second" in user_input:
            return "AC"
        elif "3" in user_input or "three" in user_input or "third" in user_input:
            return "Tatkal"
        
        return None
    
    def extract_train_number(self, user_input: str) -> Optional[str]:
        """Extract train number from input"""
        # Look for 5-digit train numbers
        numbers = re.findall(r'\b\d{5}\b', user_input)
        if numbers:
            return numbers[0]
        
        # Look for any sequence of 4-6 digits
        numbers = re.findall(r'\b\d{4,6}\b', user_input)
        if numbers:
            return numbers[0]
        
        return None
    
    def extract_pnr(self, user_input: str) -> Optional[str]:
        """Extract PNR number from input"""
        # Look for 10-digit PNR
        numbers = re.findall(r'\b\d{10}\b', user_input)
        if numbers:
            return numbers[0]
        
        # Look for word "pnr" followed by numbers
        if "pnr" in user_input.lower():
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                return numbers[0]
        
        return None
    
    def understand_context(self, user_input: str, current_state: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced context understanding
        Returns extracted information and suggested actions
        """
        context = {
            "intent": None,
            "extracted_data": {},
            "suggested_action": None,
            "confidence": 0.0
        }
        
        # Extract intent
        intent_result = self.extract_intent(user_input, current_state)
        if intent_result:
            context["intent"] = intent_result.get("intent")
            context["suggested_action"] = intent_result.get("target")
            context["confidence"] = intent_result.get("confidence", 0.0)
        
        # Extract entities
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

