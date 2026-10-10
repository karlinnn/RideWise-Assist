import json
import os
import math
from collections import Counter
import re

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_INDEX_DIR = os.path.join(_PROJECT_ROOT, "storage", "policy_index")

_STOPWORDS = {"a", "an", "the", "for", "to", "of", "and", "or", "in", "on", "at", "is", "be", "my", "me"}


def tokenize(text):
    return re.findall(r"\w+", text.lower())


def query_tokens(text):
    tokens = []
    for term in tokenize(text):
        if term in _STOPWORDS or len(term) <= 1:
            continue
        tokens.append(term)
        if len(term) > 5 and term.endswith("ing"):
            tokens.append(term[:-3])
    return tokens


def _search_text(doc):
    fname = doc.get("filename", "").replace("_", " ")
    if fname.lower().endswith(".pdf"):
        fname = fname[:-4]
    return fname + " " + doc.get("text", "")


class BM25:
    def __init__(self, corpus):
        self.corpus = corpus
        self.search_texts = [_search_text(doc) for doc in corpus]
        self.doc_len = [len(tokenize(text)) for text in self.search_texts]
        self.avgdl = sum(self.doc_len) / len(self.corpus) if self.corpus else 0
        self.tf = []
        self.df = Counter()

        for text in self.search_texts:
            tokens = tokenize(text)
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
        tokens = query_tokens(query)
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


def _result_doc(doc):
    filename = doc["filename"]
    return {
        "filename": filename,
        "source": filename,
        "page": doc["page"],
        "text": doc["text"],
    }


def load_index(index_dir=None):
    global _bm25_instance, _corpus
    if index_dir is None:
        index_dir = DEFAULT_INDEX_DIR
    path = os.path.join(index_dir, "chunks.json")
    if not os.path.exists(path):
        _corpus = []
        _bm25_instance = None
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            _corpus = json.load(f)
        if _corpus:
            _bm25_instance = BM25(_corpus)
        else:
            _bm25_instance = None
        return True
    except Exception:
        _corpus = []
        _bm25_instance = None
        return False


def _version_excluded(fname, version):
    if not version or version == "unknown":
        return False
    name = fname.lower()
    if version == "v1" and "v2" in name:
        return True
    if version == "v2" and "v1" in name:
        return True
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

        filtered = []
        for score, doc in scored_docs:
            if score <= 0:
                continue
            if _version_excluded(doc["filename"], version):
                continue
            filtered.append((score, doc))

        if not filtered:
            return []

        selected_files = []
        for _, doc in filtered:
            fn = doc["filename"]
            if fn not in selected_files:
                selected_files.append(fn)
            if len(selected_files) >= top_k:
                break

        pool = [doc for _, doc in filtered if doc["filename"] in selected_files]
        cap = max(top_k, min(len(pool), top_k * 2))
        return [_result_doc(doc) for doc in pool[:cap]]
    except Exception:
        return []
