from typing import Any, Dict

def route_after_context(state: Dict[str, Any]) -> str:
    if state.get("blocked_reason") or state.get("needs_clarification") or state.get("intent") in ("chitchat", "other"):
        return "answer"
    return "retrieval"
