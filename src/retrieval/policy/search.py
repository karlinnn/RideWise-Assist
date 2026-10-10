import json
import os
import math
from collections import Counter
import re

def tokenize(text):
    return re.findall(r'\w+', text.lower())

class BM25:
    def __init__(self, corpus):
        self.corpus = corpus
        self.doc_len = [len(tokenize(doc["text"])) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.corpus) if self.corpus else 0
        self.tf = []
        self.df = Counter()
        
        for doc in corpus:
            tokens = tokenize(doc["text"])
            tf = Counter(tokens)
            self.tf.append(tf)
            for term in tf:
                self.df[term] += 1
                
        self.N = len(corpus)
        self.idf = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))
            
    def get_scores(self, query):
        scores = [0] * self.N
        tokens = tokenize(query)
        k1 = 1.5
        b = 0.75
        for i in range(self.N):
            for term in tokens:
                if term in self.tf[i]:
                    tf = self.tf[i][term]
                    idf = self.idf.get(term, 0)
                    scores[i] += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * self.doc_len[i] / self.avgdl))
        return scores

_bm25_instance = None
_corpus = []

def load_index(index_dir="storage/policy_index"):
    global _bm25_instance, _corpus
    path = os.path.join(index_dir, "chunks.json")
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r") as f:
            _corpus = json.load(f)
        if _corpus:
            _bm25_instance = BM25(_corpus)
        return True
    except Exception:
        return False

def search_policy(query: str, version: str = None, top_k=3):
    if not _bm25_instance:
        if not load_index():
            return []
            
    if not _corpus:
        return []

    try:
        scores = _bm25_instance.get_scores(query)
        scored_docs = list(zip(scores, _corpus))
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs:
            if score <= 0:
                continue
                
            fname = doc["filename"].lower()
            if version == "v1" and "v2" in fname:
                continue
            if version == "v2" and "v1" in fname:
                continue
                
            results.append(doc)
            if len(results) >= top_k:
                break
                
        return results
    except Exception:
        return []
