import json
from src.retrieval.policy.search import search_policy, load_index
from src.graph.nodes.retrieval_node import retrieval_node

load_index()
lines = []
with open("storage/policy_index/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)
files = sorted({c["filename"] for c in chunks})
lines.append(f"chunks={len(chunks)} files={files}")

for q in ["penalty for returning rental late", "EV won't charge"]:
    res = search_policy(q)
    lines.append(f"\nSEARCH {q!r} n={len(res)}")
    for r in res:
        lines.append(f"  {r.get('source')} p{r['page']} {r['text'][:90]!r}")

for intent, q in [("penalty", "penalty for returning rental late"), ("policy", "EV won't charge")]:
    out = retrieval_node({
        "intent": intent,
        "customer_id": "CUST0001",
        "entities": {},
        "standalone_question": q,
        "evidence": [],
    })
    result = out["evidence"][0]["result"]
    names = [r["filename"] for r in result] if isinstance(result, list) else result
    lines.append(f"retrieval intent={intent} -> {names}")

open("_debug_policy_out.txt", "w", encoding="utf-8").write("\n".join(lines))
print("ok")
