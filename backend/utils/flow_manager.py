"""
Flow Manager Module

Manages IVR flow navigation and state transitions based on JSON flow definitions.
Supports both keypad input and natural language processing for intelligent navigation.

Key Features:
- Dynamic flow loading from JSON files
- State machine implementation
- Data collection and validation
- Response generation
- Flow transition management
"""

import json
import os
import sys
from typing import Dict, Any, Tuple, Optional

# Import advanced NLP
try:
    from .advanced_nlp import advanced_nlp
except ImportError:
    # Handle case when imported directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from advanced_nlp import advanced_nlp


class FlowManager:
    """Manages IVR flow navigation and state transitions"""
    
    def __init__(self, flows_dir: str = None):
        if flows_dir is None:
            # Determine flows directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.flows_dir = os.path.join(os.path.dirname(current_dir), "flows")
        else:
            self.flows_dir = flows_dir
        self.flows_cache: Dict[str, Dict[str, Any]] = {}
        self._load_all_flows()
    
    def _load_all_flows(self):
        """Load all JSON flow files into cache"""
        flow_files = [
            "train_main.json",
            "booking.json",
            "status.json",
            "schedule.json",
            "cancellation.json",
            "agent.json",
            "pnr_status.json",
            "seat_availability.json",
            "fare_enquiry.json",
            "train_between_stations.json"
        ]
        
        for flow_file in flow_files:
            flow_name = flow_file.replace(".json", "")
            try:
                flow_path = os.path.join(self.flows_dir, flow_file)
                with open(flow_path, "r", encoding="utf-8") as f:
                    self.flows_cache[flow_name] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Flow file {flow_file} not found")
            except json.JSONDecodeError as e:
                print(f"Error loading {flow_file}: {e}")
    
    def get_flow(self, flow_name: str) -> Dict[str, Any]:
        """Get a flow by name"""
        return self.flows_cache.get(flow_name, {})
    
    def process_input(
        self,
        flow: Dict[str, Any],
        current_state: str,
        user_input: str,
        is_keypad: bool,
        session: Dict[str, Any]
    ) -> Tuple[str, str, Optional[Dict[str, str]], bool]:
        """
        Process user input and return next state, message, options, and is_end flag
        
        Returns:
            (next_state, message, options, is_end)
        """
        states = flow.get("states", {})
        state_data = states.get(current_state, {})
        
        # Handle keypad input
        if is_keypad:
            transitions = state_data.get("transitions", {})
            keypad_map = state_data.get("keypad_map", {})
            
            # First, check if we need to collect data before transition
            if "actions" in state_data and "collect_data" in state_data["actions"]:
                action = state_data["actions"]["collect_data"]
                field = action.get("field", "")
                
                # Map keypad input to actual value (for class selection)
                if field == "train_class":
                    class_map = {"1": "Sleeper", "2": "AC", "3": "Tatkal"}
                    if user_input in class_map:
                        session["data"][field] = class_map[user_input]
                
                # Get next state
                target = action.get("next_state", "")
                if target.startswith("flow:"):
                    return (target, "", {}, False)
                elif target in states:
                    next_state_data = states[target]
                    return (
                        target,
                        next_state_data.get("message", ""),
                        next_state_data.get("options", {}),
                        next_state_data.get("is_end", False)
                    )
            
            # Check direct keypad mapping
            if user_input in keypad_map:
                target = keypad_map[user_input]
                if target.startswith("flow:"):
                    return (target, "", {}, False)
                elif target in states:
                    next_state_data = states[target]
                    return (
                        target,
                        next_state_data.get("message", ""),
                        next_state_data.get("options", {}),
                        next_state_data.get("is_end", False)
                    )
            
            # Check transitions
            if user_input in transitions:
                target = transitions[user_input]
                return self._follow_transition(target, states, session)
        
        # Handle speech/NLP input with intelligent processing
        else:
            # Use NLP engine for intent understanding
            nlp_result = advanced_nlp.extract_intent(user_input, current_state)
            
            # Handle greetings separately - respond naturally
            if nlp_result and nlp_result.get("type") == "greeting":
                greeting_response = nlp_result.get("response", "Hello! How can I help you?")
                # Return greeting response but stay in current state
                return (current_state, greeting_response, state_data.get("options", {}), False)
            
            # First, check if we need to collect data before transition
            if "actions" in state_data and "collect_data" in state_data["actions"]:
                action = state_data["actions"]["collect_data"]
                field = action.get("field", "")
                
                # Use advanced NLP to extract class
                if field == "train_class":
                    extracted_class = advanced_nlp.extract_class_from_speech(user_input)
                    if extracted_class:
                        session["data"][field] = extracted_class
                        target = action.get("next_state", "")
                        if target in states:
                            next_state_data = states[target]
                            return (
                                target,
                                next_state_data.get("message", ""),
                                next_state_data.get("options", {}),
                                next_state_data.get("is_end", False)
                            )
                
                # Extract train number, PNR, etc. from any input
                if field == "train_number":
                    train_num = advanced_nlp.extract_train_number(user_input)
                    if train_num:
                        session["data"][field] = train_num
                        target = action.get("next_state", "")
                        if target in states:
                            next_state_data = states[target]
                            return (
                                target,
                                next_state_data.get("message", ""),
                                next_state_data.get("options", {}),
                                next_state_data.get("is_end", False)
                            )
                
                if field == "pnr":
                    pnr = advanced_nlp.extract_pnr(user_input)
                    if pnr:
                        session["data"][field] = pnr
                        target = action.get("next_state", "")
                        if target in states:
                            next_state_data = states[target]
                            return (
                                target,
                                next_state_data.get("message", ""),
                                next_state_data.get("options", {}),
                                next_state_data.get("is_end", False)
                            )
            
            # Use Advanced NLP intent recognition
            if nlp_result and nlp_result.get("target"):
                target = nlp_result["target"]
                confidence = nlp_result.get("confidence", 0.0)
                
                if confidence > 0.7:  # High confidence match
                    return self._follow_transition(target, states, session)
            
            # Fallback to simple keyword matching for backwards compatibility
            keywords = state_data.get("keywords", {})
            for keyword, target in keywords.items():
                if keyword in user_input:
                    return self._follow_transition(target, states, session)
            
            # Check for common phrases
            speech_patterns = state_data.get("speech_patterns", {})
            for pattern, target in speech_patterns.items():
                if pattern in user_input:
                    return self._follow_transition(target, states, session)
            
            # If nothing matched, check for partial matches or similar phrases
            # This helps avoid getting stuck on slightly wrong input
            for pattern, target in speech_patterns.items():
                similarity = advanced_nlp.similarity(user_input, pattern)
                if similarity > 0.6:  # Partial match threshold
                    return self._follow_transition(target, states, session)
        
        # Handle special actions (data collection, dynamic responses)
        actions = state_data.get("actions", {})
        if "collect_data" in actions:
            field = actions["collect_data"].get("field", "")
            session["data"][field] = user_input
            
            # Move to next state after data collection
            next_state = actions["collect_data"].get("next_state", "")
            if next_state.startswith("flow:"):
                return (next_state, "", {}, False)
            elif next_state in states:
                next_state_data = states[next_state]
                next_message = next_state_data.get("message", "")
                
                # If next state also collects data, automatically show that question
                # Don't wait for another input - show the question immediately
                if "actions" in next_state_data and "collect_data" in next_state_data["actions"]:
                    # Return with the next question message
                    return (
                        next_state,
                        next_message,  # This will be spoken/displayed immediately
                        next_state_data.get("options", {}),
                        next_state_data.get("is_end", False)
                    )
                else:
                    # Next state doesn't collect data, just show message
                    return (
                        next_state,
                        next_message,
                        next_state_data.get("options", {}),
                        next_state_data.get("is_end", False)
                    )
        
        # Handle dynamic responses (train status, booking confirmation, etc.)
        if "dynamic_response" in actions:
            response_func = actions["dynamic_response"].get("function", "")
            message = self._generate_dynamic_response(response_func, session, user_input)
            next_state = actions["dynamic_response"].get("next_state", "main_menu")
            
            # Check if returning to main menu
            if next_state == "main_menu" and flow.get("name") != "train_main":
                return ("flow:train_main", "", {}, False)
            elif next_state in states:
                return (
                    next_state,
                    message,
                    states[next_state].get("options", {}),
                    states[next_state].get("is_end", False)
                )
            else:
                # Return to main menu in main flow
                main_menu = states.get("main_menu", {})
                return (
                    "main_menu",
                    message,
                    main_menu.get("options", {}),
                    False
                )
        
        # Default: invalid input - provide helpful message with graceful recovery
        if current_state == "main_menu":
            # Friendly response for invalid input in main menu
            invalid_msg = "I'm sorry, I didn't quite catch that. No worries! Let me help you: You can say things like 'book a ticket', 'check train status', 'schedule', 'cancel ticket', 'PNR status', 'seat availability', 'fare enquiry', 'trains between stations', or 'speak to agent'. Or you can press any number from 0 to 9 on the keypad. What would you like to do?"
        else:
            # Context-aware invalid message based on current state
            invalid_msg = state_data.get("invalid_input_message", 
                "I didn't quite understand that. Could you please try again? You can also say 'go back' or 'main menu' to return to the main menu, or press star on the keypad.")
            
            # Add helpful hints based on what we're trying to collect
            if "actions" in state_data and "collect_data" in state_data["actions"]:
                field = state_data["actions"]["collect_data"].get("field", "")
                if field == "train_number":
                    invalid_msg += " Please provide a 5-digit train number."
                elif field == "pnr":
                    invalid_msg += " Please provide your 10-digit PNR number."
                elif field == "train_class":
                    invalid_msg += " You can say 'Sleeper', 'AC', or 'Tatkal', or press 1, 2, or 3."
        
        return (current_state, invalid_msg, state_data.get("options", {}), False)
    
    def _follow_transition(
        self,
        target: str,
        states: Dict[str, Any],
        session: Dict[str, Any]
    ) -> Tuple[str, str, Optional[Dict[str, str]], bool]:
        """Follow a transition to a target state or flow"""
        if target.startswith("flow:"):
            # Transition to another flow
            return (target, "", {}, False)
        elif target in states:
            next_state_data = states[target]
            return (
                target,
                next_state_data.get("message", ""),
                next_state_data.get("options", {}),
                next_state_data.get("is_end", False)
            )
        else:
            # Invalid target
            return ("main_menu", "Invalid navigation. Returning to main menu.", {}, False)
    
    def _generate_dynamic_response(
        self,
        function_name: str,
        session: Dict[str, Any],
        user_input: str
    ) -> str:
        """Generate dynamic responses based on function name"""
        
        data = session.get("data", {})
        
        if function_name == "train_status":
            import random
            train_number = data.get("train_number", user_input[-5:] if len(user_input) >= 5 else "12718")
            # Simulate status with more realistic responses
            statuses = [
                ("On Time", "Great news! Train {} is running exactly on schedule."),
                ("Running 10 minutes late", "I've checked, and Train {} is running approximately 10 minutes behind schedule. Not to worry, this is a minor delay."),
                ("Running 30 minutes late", "I'm sorry to inform you that Train {} is currently running about 30 minutes late. We apologize for any inconvenience."),
                ("Delayed by 1 hour", "Unfortunately, Train {} is experiencing a delay of approximately 1 hour. We understand this is frustrating and apologize for the inconvenience.")
            ]
            status, message = random.choice(statuses)
            return message.format(train_number)
        
        elif function_name == "train_schedule":
            train_number = data.get("train_number", user_input[-5:] if len(user_input) >= 5 else "17018")
            # Simulate schedule with more details
            schedules = {
                "12718": ("8:45 AM", "5:30 PM", "8 hours 45 minutes"),
                "17018": ("6:00 AM", "2:15 PM", "8 hours 15 minutes"),
                "12009": ("7:30 AM", "1:45 PM", "6 hours 15 minutes")
            }
            times = schedules.get(train_number, ("8:00 AM", "6:00 PM", "10 hours"))
            return f"Perfect! Train {train_number} departs at {times[0]} and arrives at {times[1]}. The total journey time is {times[2]}. Is there anything else you'd like to know about this train?"
        
        elif function_name == "booking_confirmation":
            import random
            train_class = data.get("train_class", "Sleeper")
            train_number = data.get("train_number", "12718")
            pnr = random.randint(1000000000, 9999999999)
            return f"Excellent! Your booking has been confirmed successfully. You have booked a {train_class} class ticket on Train {train_number}. Your PNR number is {pnr}. Please save this PNR for future reference. Your ticket details will be sent to your registered mobile number. Is there anything else I can help you with?"
        
        elif function_name == "cancellation_confirmation":
            import random
            pnr = data.get("pnr", user_input)
            refund_amt = random.randint(500, 2000)
            return f"I've successfully cancelled your ticket with PNR {pnr}. Your refund of ₹{refund_amt} will be processed and credited back to your original payment method within 5 to 7 business days. A cancellation confirmation SMS will be sent to your registered mobile number. Thank you for using our service, and I'm sorry we couldn't accommodate your travel plans this time."
        
        elif function_name == "connect_agent":
            return "I'm connecting you to one of our customer support agents. Please hold for just a moment, and someone will be with you shortly."
        
        elif function_name == "pnr_status_response":
            import random
            pnr = data.get("pnr", user_input)
            statuses = [
                "Confirmed",
                "Waiting List (WL)",
                "Reservation Against Cancellation (RAC)",
                "Cancelled"
            ]
            status = random.choice(statuses)
            berth_info = random.choice(["Lower Berth", "Middle Berth", "Upper Berth", "Side Lower", "Side Upper"])
            coach = f"S{random.randint(1,15)}" if "Sleeper" in str(data.get("class", "")) else f"A{random.randint(1,10)}"
            return f"Thank you for your PNR {pnr}. I've checked your booking status. Your ticket is {status}. You have been assigned {berth_info} in Coach {coach}. Is there anything else I can help you with?"
        
        elif function_name == "seat_availability_response":
            import random
            train_number = data.get("train_number", "12718")
            train_class = data.get("class", "Sleeper")
            travel_date = data.get("travel_date", "Tomorrow")
            available = random.randint(5, 50)
            waiting = random.randint(0, 20)
            return f"Great! I've checked seat availability for Train {train_number} on {travel_date} in {train_class} class. There are {available} seats currently available, and {waiting} on the waiting list. Would you like to proceed with booking, or check another date?"
        
        elif function_name == "fare_response":
            import random
            train_number = data.get("train_number", "12718")
            train_class = data.get("class", "Sleeper")
            base_fares = {
                "Sleeper": random.randint(300, 800),
                "AC 3 Tier": random.randint(800, 1500),
                "AC 2 Tier": random.randint(1500, 2500),
                "First AC": random.randint(3000, 5000)
            }
            fare = base_fares.get(train_class, 500)
            return f"Thank you! The fare for Train {train_number} in {train_class} class between your selected stations is ₹{fare}. This includes base fare and reservation charges. Would you like to proceed with booking, or check another class?"
        
        elif function_name == "trains_between_stations_response":
            import random
            source = data.get("source_station", "Source")
            destination = data.get("destination_station", "Destination")
            trains = [
                ("12718", "Express", "8:45 AM", "5:30 PM", "8h 45m"),
                ("17018", "Superfast", "6:00 AM", "2:15 PM", "8h 15m"),
                ("12009", "Shatabdi", "7:30 AM", "1:45 PM", "6h 15m"),
                ("12345", "Rajdhani", "10:00 AM", "6:30 PM", "8h 30m")
            ]
            selected_trains = random.sample(trains, min(3, len(trains)))
            response = f"I found {len(selected_trains)} trains running between {source} and {destination}. "
            for i, (num, name, dep, arr, dur) in enumerate(selected_trains, 1):
                response += f"Train {num} {name} departs at {dep} and arrives at {arr}, journey time {dur}. "
            response += "Would you like more details about any specific train?"
            return response
        
        return "I'm processing your request. Please give me a moment..."
    
    def reload_flows(self):
        """Reload all flows from disk (useful for hot-reloading)"""
        self._load_all_flows()

