"""
Retrieval-Augmented Generation engine.

Uses a local sentence-transformers model (all-MiniLM-L6-v2) to embed text chunks,
stores vectors in a FAISS index on disk, and retrieves the most relevant chunks
for a given query. This runs entirely on your laptop -- no API key needed for RAG itself.
"""
import os
import json
import glob
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from config import DOCUMENTS_DIR, RAG_STORE_DIR

INDEX_PATH = os.path.join(RAG_STORE_DIR, "index.faiss")
META_PATH = os.path.join(RAG_STORE_DIR, "meta.json")

_model = None


def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def read_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def build_index_from_documents():
    """Scan DOCUMENTS_DIR, chunk every file, embed, and build a fresh FAISS index."""
    os.makedirs(RAG_STORE_DIR, exist_ok=True)
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    all_chunks = []
    metas = []
    for path in glob.glob(os.path.join(DOCUMENTS_DIR, "**", "*"), recursive=True):
        if os.path.isdir(path):
            continue
        if not path.lower().endswith((".txt", ".md", ".pdf")):
            continue
        text = read_file(path)
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append(chunk)
            metas.append({"source": os.path.basename(path), "chunk_id": i, "text": chunk})

    if not all_chunks:
        # empty index placeholder
        dim = 384  # all-MiniLM-L6-v2 output dim
        index = faiss.IndexFlatIP(dim)
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w") as f:
            json.dump([], f)
        return 0

    model = get_embedder()
    embeddings = model.encode(all_chunks, normalize_embeddings=True, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w") as f:
        json.dump(metas, f)

    return len(all_chunks)


def _load_index():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        build_index_from_documents()
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f:
        metas = json.load(f)
    return index, metas


def retrieve(query: str, top_k: int = 4):
    """Return the top_k most relevant chunks for the query, or [] if the index is empty."""
    index, metas = _load_index()
    if index.ntotal == 0 or not metas:
        return []

    model = get_embedder()
    q_emb = model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype="float32")

    scores, idxs = index.search(q_emb, min(top_k, index.ntotal))
    results = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx == -1:
            continue
        meta = metas[idx]
        results.append({"text": meta["text"], "source": meta["source"], "score": float(score)})
    return results


def add_document_and_reindex(filepath: str):
    """Called after a new file is uploaded into DOCUMENTS_DIR."""
    return build_index_from_documents()
