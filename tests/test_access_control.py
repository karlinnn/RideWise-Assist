from src.graph.workflow import run_turn

def test_unauthorized_agent():
    state = {"role": "Support Agent", "authenticated": False, "user_message": "hello"}
    res = run_turn(state)
    assert res.get("blocked_reason") == "Not authorised"
    assert "answer" not in res # because nodes weren't called
