from src.retrieval.policy.version_picker import get_applicable_version
from src.retrieval.policy.search import search_policy, tokenize, load_index
from src.graph.nodes.retrieval_node import retrieval_node
from src.graph.routing import route_after_context
import os
import json
import tempfile

def test_version_picker_v1():
    v = get_applicable_version({"booked_at": "2026-06-30 23:59:59"})
    assert v == "v1"

def test_version_picker_v2():
    v = get_applicable_version({"booked_at": "2026-07-01 00:00:01"})
    assert v == "v2"

def test_version_picker_unknown():
    v = get_applicable_version({})
    assert v == "unknown"

def test_tokenize():
    tokens = tokenize("This is a Test!")
    assert tokens == ["this", "is", "a", "test"]

def test_empty_search():
    # should return empty gracefully
    res = search_policy("does not exist query xyzxyz", top_k=3)
    assert isinstance(res, list)

def test_unsupported_version():
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "chunks.json"), "w") as f:
        json.dump([
            {"filename": "02_Cancellation_and_Refund_Policy_v1.pdf", "page": 1, "text": "hello v1 refunds"},
            {"filename": "03_Cancellation_and_Refund_Policy_v2.pdf", "page": 1, "text": "hello v2 refunds"}
        ], f)

    load_index(tmp)

    res1 = search_policy("refunds", version="v1")
    assert any("v1" in r["filename"] for r in res1)
    assert not any("v2" in r["filename"] for r in res1)

    res2 = search_policy("refunds", version="v2")
    assert any("v2" in r["filename"] for r in res2)
    assert not any("v1" in r["filename"] for r in res2)

    load_index()


def test_search_late_penalty_retrieves_schedule():
    assert load_index()
    res = search_policy("penalty for returning rental late")
    assert res, "expected non-empty policy hits"
    assert any("04_Late_Return_and_Damage_Penalty_Schedule.pdf" in r["filename"] for r in res)
    hit = next(r for r in res if "04_Late_Return" in r["filename"])
    assert hit.get("page")
    assert hit.get("text")
    assert hit.get("source") == hit["filename"]


def test_search_ev_charge_retrieves_guide():
    assert load_index()
    res = search_policy("EV won't charge")
    assert res, "expected non-empty policy hits"
    assert any("05_EV_User_Guide_and_FAQ.pdf" in r["filename"] for r in res)


def test_retrieval_routes_policy_intents_to_search():
    assert route_after_context({"intent": "policy"}) == "retrieval"
    assert route_after_context({"intent": "penalty"}) == "retrieval"
    state = {
        "intent": "penalty",
        "customer_id": "CUST0001",
        "entities": {},
        "standalone_question": "penalty for returning rental late",
        "evidence": [],
    }
    out = retrieval_node(state)
    assert out["evidence"]
    assert out["evidence"][0]["tool"] == "search_policy"
    result = out["evidence"][0]["result"]
    assert isinstance(result, list) and result
    assert any("04_Late_Return" in r["filename"] for r in result)


if __name__ == "__main__":
    test_version_picker_v1()
    test_version_picker_v2()
    test_version_picker_unknown()
    test_tokenize()
    test_empty_search()
    test_unsupported_version()
    test_search_late_penalty_retrieves_schedule()
    test_search_ev_charge_retrieves_guide()
    test_retrieval_routes_policy_intents_to_search()
    print("Policy tests passed.")
