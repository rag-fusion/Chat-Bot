from __future__ import annotations

import os
import yaml
import faiss
from typing import List, Dict
from .embeddings import embed_text  # Use unified CLIP embeddings (512-dim)
from .index_store import INDEX_PATH, connect_db
from .adapters.base import LLMAdapter
from .adapters.gpt4all_adapter import GPT4AllAdapter
from .adapters.llama_cpp_adapter import LlamaCppAdapter
from .adapters.mistral_adapter import MistralAdapter


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {"model_backend": "mistral", "model_path": None, "top_k": 5, "max_tokens": 512, "temperature": 0.2}
    return yaml.safe_load(open(path, "r"))


def build_adapter(cfg: dict) -> LLMAdapter:
    backend = (cfg.get("model_backend") or "mistral").lower()
    path = cfg.get("model_path")
    if backend == "gpt4all":
        return GPT4AllAdapter(path)
    if backend == "llama_cpp":
        return LlamaCppAdapter(path)
    return MistralAdapter(path)


def similarity_search(query: str, k: int) -> List[Dict]:
    if not os.path.exists(INDEX_PATH):
        return []
    q = embed_text(query)  # Now returns 512-dim CLIP embeddings
    index = faiss.read_index(INDEX_PATH)
    D, I = index.search(q, k)
    ids = I[0].tolist()
    scores = D[0].tolist()
    if not ids:
        return []
    conn = connect_db()
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(
        f"SELECT vector_id, page_content, file_name, file_type, page_number, timestamp, filepath FROM vectors WHERE vector_id IN ({placeholders})",
        ids,
    )
    rows = cur.fetchall()
    conn.close()
    meta_map = {r[0]: r for r in rows}
    results = []
    for vid, score in zip(ids, scores):
        r = meta_map.get(vid)
        if not r:
            continue
        results.append(
            {
                "vector_id": r[0],
                "page_content": r[1],
                "file_name": r[2],
                "file_type": r[3],
                "page_number": r[4],
                "timestamp": r[5],
                "filepath": r[6],
                "score": float(score),
            }
        )
    return results


def build_prompt(query: str, sources: List[Dict]) -> str:
    lines = []
    for i, s in enumerate(sources, start=1):
        marker = f"[{i}]"
        where = s.get("file_name")
        if s.get("file_type") == "pdf" and s.get("page_number"):
            where += f" page {s['page_number']}"
        if s.get("file_type") == "audio" and s.get("timestamp"):
            where += f" {s['timestamp']}"
        snippet = (s.get("page_content") or "").replace("\n", " ")
        lines.append(f"Source {marker} {where}: \"{snippet}\"")
    lines.append("\nAnswer the user query using only the information from sources [1..k]. Provide citations inline like [1], [2]. If the answer is unknown from sources, say you don't know.")
    lines.append(f"\nUser query: {query}\nAnswer:")
    return "\n".join(lines)


def answer_query(cfg_path: str, query: str) -> dict:
    cfg = load_config(cfg_path)
    k = int(cfg.get("top_k", 5))
    sources = similarity_search(query, k)
    prompt = build_prompt(query, sources)
    adapter = build_adapter(cfg)
    text = adapter.generate(prompt, max_tokens=int(cfg.get("max_tokens", 512)), temperature=float(cfg.get("temperature", 0.2)))
    out_sources = []
    for i, s in enumerate(sources, start=1):
        out_sources.append(
            {
                "id": i,
                "file_name": s.get("file_name"),
                "snippet": s.get("page_content"),
                "page_number": s.get("page_number"),
                "timestamp": s.get("timestamp"),
                "score": s.get("score"),
            }
        )
    return {"answer": text, "sources": out_sources}


