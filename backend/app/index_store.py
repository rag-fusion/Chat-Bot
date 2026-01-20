from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterable, List, Optional, Tuple

import faiss
import numpy as np


STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")
STORAGE_DIR = os.path.abspath(STORAGE_DIR)
INDEX_PATH = os.path.join(STORAGE_DIR, "faiss.index")
DB_PATH = os.path.join(STORAGE_DIR, "metadata.db")


def ensure_storage():
    os.makedirs(STORAGE_DIR, exist_ok=True)


def connect_db():
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vector_id INTEGER,
            page_content TEXT,
            file_name TEXT,
            file_type TEXT,
            page_number INTEGER,
            timestamp TEXT,
            filepath TEXT,
            width INTEGER,
            height INTEGER,
            bbox TEXT
        )
        """
    )
    conn.commit()
    return conn


def load_or_init_index(dim: int) -> faiss.Index:
    ensure_storage()
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    index = faiss.IndexFlatIP(dim)
    return index


def save_index(index: faiss.Index) -> None:
    ensure_storage()
    faiss.write_index(index, INDEX_PATH)


def add_embeddings_with_metadata(embeddings: np.ndarray, metadatas: List[dict]) -> int:
    if embeddings.size == 0:
        return 0
    index = load_or_init_index(embeddings.shape[1])
    # store start id
    start_id = index.ntotal
    index.add(embeddings)
    save_index(index)

    conn = connect_db()
    cur = conn.cursor()
    for i, meta in enumerate(metadatas):
        cur.execute(
            """
            INSERT INTO vectors (vector_id, page_content, file_name, file_type, page_number, timestamp, filepath, width, height, bbox)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                start_id + i,
                meta.get("page_content"),
                meta.get("file_name"),
                meta.get("file_type"),
                meta.get("page_number"),
                meta.get("timestamp"),
                meta.get("filepath"),
                meta.get("width"),
                meta.get("height"),
                meta.get("bbox"),
            ),
        )
    conn.commit()
    conn.close()
    return embeddings.shape[0]


def status() -> dict:
    index_total = 0
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        index_total = index.ntotal
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT file_name) FROM vectors")
    files_count = cur.fetchone()[0]
    conn.close()
    return {"vectors": index_total, "files": files_count}


def rebuild_from_db(dim: int) -> dict:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT rowid, page_content FROM vectors ORDER BY rowid")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        # reset empty index
        save_index(faiss.IndexFlatIP(dim))
        return {"vectors": 0}
    # Embedding requires text; images should have captions already stored in content
    texts = [r[1] or "" for r in rows]
    from .embeddings import embed_text  # Use embed_text (now CLIP-based, 512-dim)

    embs = embed_text(texts)  # Returns 512-dim embeddings
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    save_index(index)
    return {"vectors": index.ntotal}


