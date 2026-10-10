from typing import Any, Dict
from src.retrieval.db.queries import get_profile, list_bookings, get_booking, get_booking_payments, get_booking_damage_reports, get_vehicle_for_booking
from src.retrieval.policy.search import search_policy
from src.retrieval.policy.version_picker import get_applicable_version

def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    intent = state.get("intent")
    customer_id = state.get("customer_id")
    entities = state.get("entities", {})
    bid = entities.get("booking_id")
    evidence = state.get("evidence", []) or []
    needs_clarification = False

    if intent == "profile":
        res = get_profile(customer_id)
        evidence.append({"tool": "get_profile", "args": {"customer_id": customer_id}, "result": res})
        
    elif intent in ["booking_info", "payment", "damage", "vehicle"]:
        if not bid:
            res = list_bookings(customer_id)
            concise_res = [{"booking_id": b.get("booking_id"), "status": b.get("booking_status"), "start": b.get("scheduled_start")} for b in res]
            evidence.append({"tool": "list_bookings", "args": {"customer_id": customer_id}, "result": concise_res})
            needs_clarification = True
        else:
            if intent == "booking_info":
                res = get_booking(customer_id, bid)
                evidence.append({"tool": "get_booking", "args": {"booking_id": bid}, "result": res})
            elif intent == "payment":
                res = get_booking_payments(customer_id, bid)
                evidence.append({"tool": "get_booking_payments", "args": {"booking_id": bid}, "result": res})
            elif intent == "damage":
                res = get_booking_damage_reports(customer_id, bid)
                evidence.append({"tool": "get_booking_damage_reports", "args": {"booking_id": bid}, "result": res})
            elif intent == "vehicle":
                res = get_vehicle_for_booking(customer_id, bid)
                evidence.append({"tool": "get_vehicle_for_booking", "args": {"booking_id": bid}, "result": res})
                
    elif intent in ["policy", "refund", "penalty"]:
        version = "unknown"
        if bid:
            b_info = get_booking(customer_id, bid)
            if b_info and "error" not in b_info:
                version = get_applicable_version(b_info)
                
        query = state.get("standalone_question", "")
        results = search_policy(query, version=version, top_k=3)
        if results:
            evidence.append({"tool": "search_policy", "args": {"query": query, "version": version}, "result": results})
        else:
            evidence.append({"tool": "search_policy", "args": {"query": query, "version": version}, "result": "No matching policy found."})
        
    return {"evidence": evidence, "needs_clarification": needs_clarification}
