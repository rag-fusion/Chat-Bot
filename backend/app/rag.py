from __future__ import annotations

import os
import yaml
from typing import List, Dict, Any, Optional

from .retriever import get_retriever
from .llm import build_adapter, load_config
# from .llm.prompts import build_prompt # We will build custom prompt here for citation binding
from .llm.adapter import LLMAdapter

def answer_query(cfg_path: str, query: str, chat_id: str, session_files: Optional[List[str]] = None) -> dict:
    """
    Answer a query using the RAG pipeline with session context and strict citation binding.
    """
    # Load config
    cfg = load_config(cfg_path)
    
    # Retrieve with relevance threshold and session context
    k = int(cfg.get("top_k", 15))
    min_score = float(cfg.get("min_relevance_score", 0.65))
    
    retriever = get_retriever()
    
    # Pass chat_id to retrieve
    sources = retriever.retrieve(
        query, 
        chat_id=chat_id,
        top_k=k, 
        min_score=min_score,
        session_files=session_files
    )
    
    # Handle no relevant sources found
    if not sources:
        return {
            "answer": "I don't have enough relevant information in the uploaded documents to answer this question.",
            "sources": []
        }
    
    # Build Structured Context & Citation Map
    context_parts = []
    citation_map = {} # citation_number -> vector_id needed for frontend link
    out_sources = []
    
    for i, s in enumerate(sources, start=1):
        # Format: [1] (File: doc.pdf, Page: 2) Content...
        content = s.get("page_content") or s.get("content", "")
        file_name = s.get("file_name", "Unknown File")
        page_num = s.get("page_number", "?")
        modality = s.get("modality", "text")
        
        # Store for frontend
        citation_entry = {
            "id": i,
            "vector_id": s.get("vector_id"), # Crucial for viewer
            "file_name": file_name,
            "snippet": content[:200] + "...", # Preview
            "page_number": page_num,
            "score": s.get("score"),
            "modality": modality
        }
        out_sources.append(citation_entry)
        citation_map[i] = citation_entry
        
        # Add to LLM Context
        context_parts.append(f"[{i}] (File: {file_name}, Type: {modality}) {content}")
        
    context_str = "\n\n".join(context_parts)
    
    # Build Prompt with Explicit Instructions
    system_prompt = (
        "You are a helpful AI assistant. Answer the user's question based ONLY on the provided context below.\n"
        "Cite the sources you use by their number, e.g. [1] or [2].\n"
        "If the answer is not in the context, say you don't know.\n"
        "Do not invent information."
    )
    
    user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Generate
    adapter = build_adapter(cfg)
    text = adapter.generate(
        full_prompt, 
        max_tokens=int(cfg.get("max_tokens", 512)), 
        temperature=float(cfg.get("temperature", 0.2)) # Low temp for factual answers
    )
    
    # Post-processing could verify citations here, but for now we trust LLM + clickable links
    
    return {"answer": text, "sources": out_sources}
