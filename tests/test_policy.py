from unittest.mock import patch
from src.retrieval.policy.version_picker import get_applicable_version
from src.retrieval.policy.search import search_policy, tokenize, load_index
import os
import json

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
    if not os.path.exists("storage/policy_index"):
        os.makedirs("storage/policy_index")
    with open("storage/policy_index/chunks.json", "w") as f:
        json.dump([
            {"filename": "02_Cancellation_and_Refund_Policy_v1.pdf", "page": 1, "text": "hello v1 refunds"},
            {"filename": "03_Cancellation_and_Refund_Policy_v2.pdf", "page": 1, "text": "hello v2 refunds"}
        ], f)
    
    # Reload index
    load_index()
    
    res1 = search_policy("refunds", version="v1")
    assert any("v1" in r["filename"] for r in res1)
    assert not any("v2" in r["filename"] for r in res1)
    
    res2 = search_policy("refunds", version="v2")
    assert any("v2" in r["filename"] for r in res2)
    assert not any("v1" in r["filename"] for r in res2)

if __name__ == "__main__":
    test_version_picker_v1()
    test_version_picker_v2()
    test_version_picker_unknown()
    test_tokenize()
    test_empty_search()
    test_unsupported_version()
    print("Policy tests passed.")
