import pytest
from unittest.mock import patch, MagicMock
from src.graph.nodes.context_node import context_node
from src.graph.nodes.retrieval_node import retrieval_node
from src.graph.nodes.answer_node import answer_node
from src.session import Session
from src.retrieval.db.queries import get_booking

class DummyRes:
    def __init__(self, content):
        self.content = content

def test_malformed_llm_output():
    state = {"user_message": "hello", "history": [], "entities": {}}
    # Mock LLM to return malformed output
    with patch("src.graph.nodes.context_node.chat", return_value=DummyRes("{malformed json...")):
        res = context_node(state)
        assert res["intent"] == "other"
        assert res["entities"]["booking_id"] is None

def test_clarification():
    # When intent is booking_info and no booking_id is provided, retrieval_node should set needs_clarification
    state = {"intent": "booking_info", "customer_id": "CUST0001", "entities": {}, "evidence": []}
    
    with patch("src.graph.nodes.retrieval_node.list_bookings", return_value=[{"booking_id": "B-0001", "booking_status": "UPC"}]):
        res = retrieval_node(state)
        assert res["needs_clarification"] is True
        assert len(res["evidence"]) == 1
        assert res["evidence"][0]["tool"] == "list_bookings"
        assert res["evidence"][0]["result"] == [{"booking_id": "B-0001", "status": "UPC", "start": None}]

def test_session_reset():
    sess = Session()
    sess.customer_id = "CUST1"
    sess.active_booking_id = "B-0001"
    sess.history = [{"role": "user", "content": "hello"}]
    
    # Normal reset
    sess.reset()
    assert sess.customer_id == "CUST1" # shouldn't clear ID
    assert sess.history == []
    assert sess.active_booking_id is None
    
    # Hard reset
    sess.history = [{"role": "user", "content": "hi"}]
    sess.active_booking_id = "B-0002"
    sess.hard_reset()
    assert sess.customer_id == ""
    assert sess.history == []
    assert sess.active_booking_id is None

def test_cross_customer_booking_access():
    # Assuming get_booking enforces customer ownership
    with patch("src.retrieval.db.connection.get_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
        res = get_booking("CUST2", "B-CUST1")
        assert res == {"error": "not_found"}

def test_invalid_booking_id():
    with patch("src.retrieval.db.connection.get_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
        res = get_booking("CUST1", "B-INVALID")
        assert res == {"error": "not_found"}

def test_missing_evidence():
    state = {"evidence": [{"tool": "get_booking", "result": {"error": "not_found"}}], "needs_clarification": False, "user_message": "what is my booking?"}
    with patch("src.graph.nodes.answer_node.chat", return_value=DummyRes("I don't have that information.")):
        res = answer_node(state)
        assert "I don't have that information." in res["answer"]

def test_answer_llm_error():
    state = {"evidence": [], "needs_clarification": False, "user_message": "hi"}
    with patch("src.graph.nodes.answer_node.chat", return_value={"error": "failed"}):
        res = answer_node(state)
        assert res["answer"] == "I'm having trouble retrieving that information right now. Please try again later."
