import json
import re
from typing import Any, Dict
from src.llm import chat

VALID_INTENTS = {"booking_info", "payment", "damage", "vehicle", "profile", "policy", "refund", "penalty", "chitchat", "other"}

def normalize_booking_id(bid):
    if not bid:
        return None
    return str(bid).strip().upper()

def context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_message = state.get("user_message", "")
    history = state.get("history", [])[-6:]
    entities = state.get("entities", {})
    active_booking_id = entities.get("active_booking_id")
    
    prompt = f"""Analyze the user message and conversation history. Return JSON only:
{{
    "standalone_question": "<str>",
    "intent": "<booking_info|payment|damage|vehicle|profile|policy|refund|penalty|chitchat|other>",
    "booking_id": "<str|null>"
}}

User message: {user_message}
History: {json.dumps(history)}
Active booking ID: {active_booking_id}"""

    res = chat([{"role": "user", "content": prompt}])
    
    intent = "other"
    sq = user_message
    bid = None
    
    try:
        if isinstance(res, dict) and "error" in res:
            raise ValueError("LLM Error")
        text = res.content.strip()
        text = re.sub(r"^```(json)?|```$", "", text).strip()
        data = json.loads(text)
        
        intent = data.get("intent", "other")
        if intent not in VALID_INTENTS:
            intent = "other"
            
        sq = data.get("standalone_question", user_message)
        bid = data.get("booking_id")
    except Exception:
        intent = "other"
        
    bid = normalize_booking_id(bid)
    
    # Preserve active booking id if applicable
    if not bid and intent in {"booking_info", "payment", "damage", "vehicle"}:
        bid = active_booking_id
        
    if not bid:
        bid = active_booking_id
        
    return {
        "intent": intent, 
        "standalone_question": sq, 
        "entities": {"booking_id": bid, "active_booking_id": bid}
    }
