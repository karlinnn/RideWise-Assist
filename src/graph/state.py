from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict, total=False):
    role: str
    customer_id: str
    user_message: str
    history: List[Dict[str, str]]
    standalone_question: str
    intent: str
    entities: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    needs_clarification: bool
    blocked_reason: Optional[str]
    answer: str
    authenticated: bool
    agent_name: Optional[str]
