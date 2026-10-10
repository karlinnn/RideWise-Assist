import os
import json
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes.context_node import context_node
from src.graph.nodes.retrieval_node import retrieval_node
from src.graph.nodes.answer_node import answer_node
from src.graph.routing import route_after_context

def build_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("context", context_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("answer", answer_node)
    
    workflow.set_entry_point("context")
    workflow.add_conditional_edges("context", route_after_context, {"answer": "answer", "retrieval": "retrieval"})
    workflow.add_edge("retrieval", "answer")
    workflow.add_edge("answer", END)
    
    return workflow.compile()

graph = build_workflow()

def run_turn(state):
    if state.get("role") in ("agent", "Support Agent") and not state.get("authenticated"):
        res = dict(state)
        res["blocked_reason"] = "Not authorised"
        return res
        
    out = graph.invoke(state)
    
    if state.get("role") in ("agent", "Support Agent"):
        os.makedirs("storage", exist_ok=True)
        with open("storage/audit_log.jsonl", "a") as f:
            log_line = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": state.get("agent_name"),
                "question": state.get("user_message"),
                "intents": out.get("intent"),
                "tools_called": [t.get("tool") for t in out.get("evidence", [])]
            }
            f.write(json.dumps(log_line) + "\n")
            
    return out
