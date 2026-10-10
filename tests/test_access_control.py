from src.graph.workflow import run_turn
from src.retrieval.db.queries import get_booking, get_booking_payments, get_booking_damage_reports, list_bookings

def test_unauthorized_agent():
    state = {"role": "Support Agent", "authenticated": False, "user_message": "hello"}
    res = run_turn(state)
    assert res.get("blocked_reason") == "Not authorised"
    assert "answer" not in res

def test_authenticated_agent_query():
    state = {"role": "Support Agent", "authenticated": True, "agent_name": "Alice", "user_message": "Is B-1234 on time?", "entities": {"booking_id": "B-1234"}}
    res = run_turn(state)
    assert res.get("blocked_reason") is None
    assert "answer" in res

def test_agent_database_bypass_customer_id():
    # Simulate agent checking bookings where customer_id is None
    res = get_booking(None, "B-TEST")
    assert type(res) == dict # Could be error not found, but it won't crash on ownership check
    
    pay_res = get_booking_payments(None, "B-TEST")
    assert type(pay_res) == list or "error" in pay_res
    
    dmg_res = get_booking_damage_reports(None, "B-TEST")
    assert type(dmg_res) == list or "error" in dmg_res
    
    lst_res = list_bookings(None)
    assert type(lst_res) == list
