import json
import math
import re
from collections import Counter

STOPWORDS = {"a", "an", "the", "for", "to", "of", "and", "or", "in", "on", "at", "is", "be", "my", "me"}

def stem(tok):
    if len(tok) > 5 and tok.endswith("ing"):
        return tok[:-3]
    if len(tok) > 4 and tok.endswith("ed"):
        return tok[:-2]
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok

def tokenize(text):
    toks = re.findall(r"\w+", text.lower())
    out = []
    for t in toks:
        if t in STOPWORDS or len(t) <= 1:
            continue
        out.append(stem(t))
    return out

with open("storage/policy_index/chunks.json", encoding="utf-8") as f:
    corpus = json.load(f)

def indexed_text(c, repeats=3):
    name = c["filename"].replace("_", " ").replace(".pdf", "")
    return (name + " ") * repeats + c["text"]

index_texts = [indexed_text(c) for c in corpus]
doc_len = [len(tokenize(t)) for t in index_texts]
avgdl = sum(doc_len) / len(corpus)
tfs = []
df = Counter()
for t in index_texts:
    tokens = tokenize(t)
    tf = Counter(tokens)
    tfs.append(tf)
    for term in tf:
        df[term] += 1
N = len(corpus)
idf = {term: math.log(1 + (N - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}

def scores(query):
    sc = [0] * N
    k1, b = 1.5, 0.75
    qtoks = tokenize(query)
    for i in range(N):
        for term in qtoks:
            if term in tfs[i]:
                tf = tfs[i][term]
                sc[i] += idf.get(term, 0) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len[i] / avgdl))
    return sc

lines = []
for q in ["penalty for returning rental late", "EV won't charge"]:
    lines.append("QUERY " + q + " tokens " + str(tokenize(q)))
    ranked = sorted(zip(scores(q), corpus), key=lambda x: -x[0])
    for sc, doc in ranked[:8]:
        lines.append(f"  {sc:.4f} {doc['filename']} p{doc['page']}")

open("_debug_search_hyp.txt", "w", encoding="utf-8").write("\n".join(lines))
print("ok")
