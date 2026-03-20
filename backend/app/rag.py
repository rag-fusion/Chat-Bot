from __future__ import annotations

import re
import logging
import os
import yaml
from typing import List, Dict, Any, Optional

from .retriever import get_retriever
from .llm import build_adapter, load_config
from .llm.adapter import LLMAdapter

logger = logging.getLogger(__name__)
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
        logger.info(f"[RAG] chat_id={chat_id} — no relevant sources found")
        return {
            "answer": "I don't have enough relevant information in the uploaded documents to answer this question.",
            "sources": [],
            "citation_map": {}
        }
    
    # Build Structured Context & Citation Map
    context_parts = []
    citation_map = {}
    out_sources = []
    
    for i, s in enumerate(sources, start=1):
        content = s.get("page_content") or s.get("content", "")
        file_name = s.get("file_name", "Unknown File")
        page_num = s.get("page_number", "?")
        modality = s.get("modality", "text")
        vector_id = s.get("vector_id")
        
        citation_entry = {
            "id": i,
            "vector_id": vector_id,
            "session_id": chat_id,
            "file_name": file_name,
            "snippet": content[:200] + ("..." if len(content) > 200 else ""),
            "page_number": page_num,
            "score": s.get("score"),
            "modality": modality
        }
        out_sources.append(citation_entry)
        citation_map[i] = citation_entry
        
        # LLM Context with structured format
        context_parts.append(
            f"[{i}] file={file_name} page={page_num} vector_id={vector_id}\n{content}"
        )
        
    context_str = "\n\n".join(context_parts)
    
    # Strict extraction prompt — do not infer, only extract
    system_prompt = (
        "You are a precise document extraction assistant. Follow these rules STRICTLY:\n"
        "1. Answer ONLY using text that is EXPLICITLY written in the context below.\n"
        "2. Do NOT infer, guess, summarize, or paraphrase. Extract the exact answer.\n"
        "3. If the exact answer is not explicitly present in the context, say: "
        "\"The exact answer is not found in the uploaded documents.\"\n"
        "4. Cite ONLY the specific chunk(s) you extract the answer from, using [1], [2], etc.\n"
        "5. Do NOT cite chunks you did not use.\n"
        "6. Keep your answer short and direct."
    )
    
    user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Generate
    adapter = build_adapter(cfg)
    text = adapter.generate(
        full_prompt, 
        max_tokens=int(cfg.get("max_tokens", 512)), 
        temperature=float(cfg.get("temperature", 0.1))
    )
    
    # Prune citations: only keep sources that are actually cited in the answer
    used_ids = set()
    for match in re.finditer(r'\[(\d+)\]', text):
        used_ids.add(int(match.group(1)))
    
    if used_ids:
        pruned_sources = [s for s in out_sources if s["id"] in used_ids]
    else:
        # If LLM cited nothing but gave an answer, keep top 1 source as context
        pruned_sources = out_sources[:1] if out_sources else []
    
    pruned_map = {s["id"]: s for s in pruned_sources}
    
    logger.info(
        f"[RAG] chat_id={chat_id} retrieved={len(out_sources)} "
        f"cited_ids={used_ids} pruned_to={len(pruned_sources)}"
    )
    
    return {"answer": text, "sources": pruned_sources, "citation_map": pruned_map}
