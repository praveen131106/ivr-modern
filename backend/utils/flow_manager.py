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
    
    def handle_subflow_transition(
        self,
        target_flow_name: str,
        session: Dict[str, Any],
        user_input: str
    ) -> Tuple[str, str, Optional[Dict[str, str]], bool]:
        """Perform intelligent slot filling and instant resolution when entering subflows"""
        target_flow = self.get_flow(target_flow_name)
        if not target_flow:
            session["current_flow"] = "train_main"
            session["current_state"] = "main_menu"
            main_flow = self.get_flow("train_main")
            options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
            return ("main_menu", "Requested flow not found. Returning to main menu.", options, False)

        initial_state = target_flow.get("initial_state", "main_menu")
        session["current_flow"] = target_flow_name
        session["current_state"] = initial_state
        
        # 1. Slot extraction & instant confirmation for booking flow
        if target_flow_name == "booking":
            cls = advanced_nlp.extract_class_from_speech(user_input)
            train = advanced_nlp.extract_train_number(user_input)
            
            if cls:
                session["data"]["train_class"] = cls
            if train:
                session["data"]["train_number"] = train
                
            # If both class and train number/name are present, confirm booking instantly!
            if session["data"].get("train_class") and session["data"].get("train_number"):
                msg = self._generate_dynamic_response("booking_confirmation", session, user_input)
                session["current_flow"] = "train_main"
                session["current_state"] = "main_menu"
                main_flow = self.get_flow("train_main")
                options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
                return ("main_menu", msg, options, False)
                
            # If only class is present, prompt for train number
            elif session["data"].get("train_class"):
                session["current_state"] = "collect_train_number"
                msg = f"Perfect! I've selected {session['data']['train_class']} class. Now, please enter or tell me the train number or train name you'd like to book."
                return ("collect_train_number", msg, {}, False)
                
            # If only train is present, prompt for class
            elif session["data"].get("train_number"):
                session["current_state"] = "select_class"
                msg = f"Great! I'd be happy to help you book a ticket for {session['data']['train_number']}. Which class would you like? Press 1 for Sleeper, Press 2 for AC 3 Tier, or Press 3 for Tatkal."
                options = target_flow.get("states", {}).get("select_class", {}).get("options", {})
                return ("select_class", msg, options, False)

        # 2. Slot extraction for status check
        elif target_flow_name == "status":
            train = advanced_nlp.extract_train_number(user_input)
            if train:
                session["data"]["train_number"] = train
                msg = self._generate_dynamic_response("train_status", session, user_input)
                session["current_flow"] = "train_main"
                session["current_state"] = "main_menu"
                main_flow = self.get_flow("train_main")
                options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
                return ("main_menu", msg, options, False)

        # 3. Slot extraction for schedule check
        elif target_flow_name == "schedule":
            train = advanced_nlp.extract_train_number(user_input)
            if train:
                session["data"]["train_number"] = train
                msg = self._generate_dynamic_response("train_schedule", session, user_input)
                session["current_flow"] = "train_main"
                session["current_state"] = "main_menu"
                main_flow = self.get_flow("train_main")
                options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
                return ("main_menu", msg, options, False)

        # 4. Slot extraction for PNR status
        elif target_flow_name == "pnr_status":
            pnr = advanced_nlp.extract_pnr(user_input)
            if pnr and pnr.isdigit() and len(pnr) == 10:
                session["data"]["pnr"] = pnr
                msg = self._generate_dynamic_response("pnr_status_response", session, user_input)
                session["current_flow"] = "train_main"
                session["current_state"] = "main_menu"
                main_flow = self.get_flow("train_main")
                options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
                return ("main_menu", msg, options, False)

        # 5. Slot extraction for cancellation
        elif target_flow_name == "cancellation":
            pnr = advanced_nlp.extract_pnr(user_input)
            if pnr and pnr.isdigit() and len(pnr) == 10:
                session["data"]["pnr"] = pnr
                msg = self._generate_dynamic_response("cancellation_confirmation", session, user_input)
                session["current_flow"] = "train_main"
                session["current_state"] = "main_menu"
                main_flow = self.get_flow("train_main")
                options = main_flow.get("states", {}).get("main_menu", {}).get("options", {})
                return ("main_menu", msg, options, False)

        # Default fallback to flow initial state message
        state_data = target_flow.get("states", {}).get(initial_state, {})
        msg = state_data.get("message", f"Welcome to {target_flow_name} service.")
        options = state_data.get("options", {})
        is_end = state_data.get("is_end", False)
        return (initial_state, msg, options, is_end)
    
    def _execute_transition(
        self,
        flow: Dict[str, Any],
        target_state: str,
        session: Dict[str, Any],
        user_input: str
    ) -> Tuple[str, str, Optional[Dict[str, str]], bool]:
        """Execute state transition and resolve any dynamic responses or data collection prompts"""
        if target_state.startswith("flow:"):
            return (target_state, "", {}, False)
            
        # Auto-resolve booking completion if both class & train number/name are present
        if session.get("data", {}).get("train_class") and session.get("data", {}).get("train_number"):
            if target_state in ["collect_train_number", "select_class", "confirm_booking"]:
                target_state = "confirm_booking"

        states = flow.get("states", {})
        if target_state not in states:
            return ("flow:train_main", "Returning to main menu.", {}, False)
            
        state_data = states[target_state]
        actions = state_data.get("actions", {})
        
        if "dynamic_response" in actions:
            func_name = actions["dynamic_response"].get("function", "")
            message = self._generate_dynamic_response(func_name, session, user_input)
            next_s = actions["dynamic_response"].get("next_state", "main_menu")
            
            if next_s.startswith("flow:"):
                return (next_s, message, {}, False)
            elif next_s == "main_menu" and flow.get("name") != "train_main":
                return ("flow:train_main", message, {}, False)
            elif next_s in states:
                ns_data = states[next_s]
                return (next_s, message, ns_data.get("options", {}), ns_data.get("is_end", False))
            else:
                return ("main_menu", message, {}, False)
                
        return (
            target_state,
            state_data.get("message", ""),
            state_data.get("options", {}),
            state_data.get("is_end", False)
        )

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
        
        target_state = None
        
        # 1. Handle Keypad Input
        if is_keypad:
            transitions = state_data.get("transitions", {})
            keypad_map = state_data.get("keypad_map", {})
            
            # Check if collect_data is active in current state
            if "actions" in state_data and "collect_data" in state_data["actions"]:
                action = state_data["actions"]["collect_data"]
                field = action.get("field", "")
                
                if field == "train_class":
                    class_map = {"1": "Sleeper", "2": "AC", "3": "Tatkal"}
                    session["data"][field] = class_map.get(user_input, user_input)
                else:
                    session["data"][field] = user_input
                    
                target_state = action.get("next_state", "")
            
            elif user_input in keypad_map:
                target_state = keypad_map[user_input]
            elif user_input in transitions:
                target_state = transitions[user_input]
                
        # 2. Handle Speech/NLP Input
        else:
            nlp_result = advanced_nlp.extract_intent(user_input, current_state)
            
            if nlp_result and nlp_result.get("type") == "greeting":
                greeting_response = nlp_result.get("response", "Hello! How can I help you?")
                return (current_state, greeting_response, state_data.get("options", {}), False)
                
            if "actions" in state_data and "collect_data" in state_data["actions"]:
                action = state_data["actions"]["collect_data"]
                field = action.get("field", "")
                
                extracted_val = None
                if field == "train_class":
                    extracted_val = advanced_nlp.extract_class_from_speech(user_input)
                elif field == "train_number":
                    extracted_val = advanced_nlp.extract_train_number(user_input)
                elif field == "pnr":
                    extracted_val = advanced_nlp.extract_pnr(user_input)
                    
                if extracted_val:
                    session["data"][field] = extracted_val
                    target_state = action.get("next_state", "")
                elif field not in ["train_number", "pnr", "train_class"]:
                    session["data"][field] = user_input
                    target_state = action.get("next_state", "")
                
            if not target_state and nlp_result and nlp_result.get("target"):
                if nlp_result.get("confidence", 0.0) > 0.7:
                    target_state = nlp_result["target"]
                    
            if not target_state:
                keywords = state_data.get("keywords", {})
                for k, t in keywords.items():
                    if k in user_input:
                        target_state = t
                        break
                        
            if not target_state:
                speech_patterns = state_data.get("speech_patterns", {})
                for p, t in speech_patterns.items():
                    if p in user_input:
                        target_state = t
                        break
                        
            if not target_state:
                for p, t in speech_patterns.items():
                    if advanced_nlp.similarity(user_input, p) > 0.6:
                        target_state = t
                        break

        # 3. Process Target State Transition if resolved
        if target_state:
            return self._execute_transition(flow, target_state, session, user_input)
            
        # 4. If current state itself has dynamic_response (e.g. initial_state)
        if "actions" in state_data and "dynamic_response" in state_data["actions"]:
            return self._execute_transition(flow, current_state, session, user_input)

        # 5. Default: invalid input - provide helpful message with graceful recovery
        if current_state == "main_menu":
            invalid_msg = "I'm sorry, I didn't quite catch that. No worries! Let me help you: You can say things like 'book a ticket', 'check train status', 'schedule', 'cancel ticket', 'PNR status', 'seat availability', 'fare enquiry', 'trains between stations', or 'speak to agent'. Or you can press any number from 0 to 9 on the keypad. What would you like to do?"
        else:
            invalid_msg = state_data.get("invalid_input_message", 
                "I didn't quite understand that. Could you please try again? You can also say 'go back' or 'main menu' to return to the main menu, or press star on the keypad.")
            
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
        return self._execute_transition({"states": states, "name": ""}, target, session, "")
    
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
            train_input = data.get("train_number", user_input if user_input else "12718")
            
            train_names = {
                "12718": "12718 Godavari Express",
                "17018": "17018 Secunderabad Express",
                "12009": "12009 Shatabdi Express",
                "12345": "12345 Rajdhani Express",
                "godavari": "12718 Godavari Express",
                "secunderabad": "17018 Secunderabad Express",
                "shatabdi": "12009 Shatabdi Express",
                "rajdhani": "12345 Rajdhani Express"
            }
            train_display = train_names.get(train_input.lower(), f"Train {train_input}")
            pnr = str(random.randint(1000000000, 9999999999))
            
            booking_obj = {
                "pnr": pnr,
                "train_display": train_display,
                "train_class": train_class,
                "status": "CONFIRMED",
                "fare": random.randint(450, 1850)
            }
            if "user_bookings" not in session["data"]:
                session["data"]["user_bookings"] = []
            session["data"]["user_bookings"].append(booking_obj)
            session["data"]["last_booked_pnr"] = pnr
            
            return f"Excellent! Your booking has been confirmed successfully. You have booked a {train_class} class ticket on {train_display}. Your generated PNR number is {pnr}. This booking has been saved to your account. Is there anything else I can help you with?"
        
        elif function_name == "cancellation_confirmation":
            import random
            user_bookings = session.get("data", {}).get("user_bookings", [])
            active_bookings = [b for b in user_bookings if b.get("status") == "CONFIRMED"]
            
            pnr_input = data.get("pnr", user_input)
            matched_booking = None
            
            for b in active_bookings:
                if b["pnr"] in user_input or pnr_input in b["pnr"] or b["train_display"].lower() in user_input.lower():
                    matched_booking = b
                    break
            
            if not matched_booking and active_bookings:
                matched_booking = active_bookings[-1]
            
            if matched_booking:
                matched_booking["status"] = "CANCELLED"
                refund_amt = matched_booking.get("fare", random.randint(500, 1500))
                return f"I have successfully cancelled your booking for {matched_booking['train_display']} with PNR {matched_booking['pnr']}. Your full refund of ₹{refund_amt} has been initiated back to your original payment method. Thank you for using our train enquiry system!"
            else:
                refund_amt = random.randint(500, 1500)
                pnr_display = pnr_input if pnr_input else "1000000000"
                return f"I've successfully cancelled your ticket with PNR {pnr_display}. Your refund of ₹{refund_amt} will be processed within 3-5 business days. Is there anything else I can assist you with?"
        
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

