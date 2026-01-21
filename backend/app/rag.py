from __future__ import annotations

import os
import yaml
from typing import List, Dict, Any

from .retriever import get_retriever
from .llm import build_adapter, load_config
from .llm.prompts import build_prompt
from .llm.adapter import LLMAdapter

def similarity_search(query: str, k: int) -> List[Dict]:
    """Deprecated: Use retriever.retrieve directly."""
    retriever = get_retriever()
    return retriever.retrieve(query, top_k=k)

def answer_query(cfg_path: str, query: str) -> dict:
    """Answer a query using the RAG pipeline."""
    # Load config
    cfg = load_config(cfg_path)
    
    # Retrieve
    k = int(cfg.get("top_k", 5))
    retriever = get_retriever()
    sources = retriever.retrieve(query, top_k=k)
    
    # Build prompt
    prompt = build_prompt(query, sources)
    
    # Generate
    adapter = build_adapter(cfg)
    text = adapter.generate(
        prompt, 
        max_tokens=int(cfg.get("max_tokens", 512)), 
        temperature=float(cfg.get("temperature", 0.2))
    )
    
    # Format sources for output
    out_sources = []
    for i, s in enumerate(sources, start=1):
        out_sources.append({
            "id": i,
            "file_name": s.get("file_name"),
            "snippet": s.get("content") or s.get("page_content"), # aligned with retriever output
            "page_number": s.get("page_number"),
            "timestamp": s.get("timestamp"),
            "score": s.get("score"),
            "modality": s.get("modality")
        })
        
    return {"answer": text, "sources": out_sources}


