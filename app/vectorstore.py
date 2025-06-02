# app/vectorstore.py
import faiss
import numpy as np

# 384 dims for all-MiniLM-L6-v2
DIM = 384
index = faiss.IndexFlatIP(DIM)
profiles = []   # keep track of {id, metadata}

def add_profile(id: str, embedding: np.ndarray, metadata: dict):
    index.add(np.array([embedding]))
    profiles.append({"id": id, **metadata})

def search(query_emb: np.ndarray, top_k: int = 5):
    D, I = index.search(np.array([query_emb]), top_k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        md = profiles[idx]
        md["score"] = float(dist)
        results.append(md)
    return results
