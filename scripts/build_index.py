import sys
import os

# add project root to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.policy.ingest import build_index

if __name__ == "__main__":
    print("Building policy index...")
    build_index()
    print("Done.")
