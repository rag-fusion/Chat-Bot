"""
Enhanced retrieval with reranking, session isolation, and NTRO safeguards.
"""

from __future__ import annotations

import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from ..embeddings import embed_text
from ..vector_store import get_store

logger = logging.getLogger(__name__)


class Retriever:
    """Enhanced retriever with session isolation and reranking."""
    
    def __init__(self, store=None):
        self.store = store or get_store()
    
    def retrieve(self, 
                 query_text: str, 
                 chat_id: str,
                 top_k: int = 10, 
                 modality_filter: Optional[str] = None, 
                 min_score: float = 0.65, 
                 session_files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve and rerank results for a query within a specific session.
        
        Args:
            query_text: The search query.
            chat_id: The session/chat ID to search within.
            top_k: Number of results to return.
            modality_filter: Optional filter for 'text', 'image', etc.
            min_score: Minimum similarity score (cosine similarity since normalized).
            session_files: (Deprecated/Legacy) prioritized files.
        """
        if not chat_id:
            logger.warning("[RETRIEVE] No chat_id provided — returning empty")
            return []

        logger.info(f"[RETRIEVE] chat_id={chat_id} query={query_text[:80]}... top_k={top_k} min_score={min_score}")

        # 1. Generate query embedding
        query_embedding = embed_text(query_text)
        
        # 2. Search in Session Index — fetch modest candidates for filtering
        search_k = min(top_k * 3, 30) 
        
        try:
            results = self.store.search(query_embedding, search_k, session_id=chat_id)
        except Exception as e:
            logger.error(f"[RETRIEVE] Search error for session {chat_id}: {e}")
            return []
        
        # 3. Filter by Modality
        if modality_filter:
            results = [r for r in results if r.get('modality') == modality_filter]
        
        # 4. Filter by Score Threshold (NTRO Requirement)
        filtered = [r for r in results if r.get('score', 0) >= min_score]
        
        logger.info(f"[RETRIEVE] chat_id={chat_id} raw_results={len(results)} after_threshold={len(filtered)} (min_score={min_score})")
        
        if not filtered:
            return []
        
        # 5. Rerank Results
        reranked = self.rerank_results(query_text, filtered)
        
        final = reranked[:top_k]
        logger.info(f"[RETRIEVE] chat_id={chat_id} returning {len(final)} results, vector_ids={[r.get('vector_id') for r in final]}")
        return final
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using multiple signals, with heading/label preference."""
        if not results:
            return results
        
        query_lower = query.lower()
        # Detect if query asks for a heading/label value
        heading_query = any(kw in query_lower for kw in [
            'title', 'name', 'project', 'heading', 'problem statement',
            'abstract', 'summary', 'objective', 'introduction', 'conclusion'
        ])
        
        for result in results:
            score = result.get('score', 0.0)
            content = (result.get('page_content') or result.get('content', '')).lower()
            
            # Boost for exact query match in content
            if query_lower in content:
                score += 0.1
            
            # Boost for heading/label content when query looks for headings
            if heading_query:
                import re
                # Check if chunk contains heading-like patterns
                if re.search(r'(?:title|project\s*name|problem\s*statement)\s*[:—\-]', content, re.IGNORECASE):
                    score += 0.15
                # Boost first-page chunks (titles usually on page 1)
                if result.get('page_number') == 1:
                    score += 0.05
            
            # Boost for file name match
            file_name = result.get('file_name', '').lower()
            if any(word in file_name for word in query_lower.split()):
                score += 0.05
            
            # Boost for images
            if result.get('modality') == 'image':
                score += 0.03
            
            result['rerank_score'] = score
        
        results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        return results

# Global retriever instance
_retriever_instance: Optional[Retriever] = None

def get_retriever() -> Retriever:
    """Get global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance

def retrieve(query_text: str, chat_id: str, top_k: int = 10, modality_filter: Optional[str] = None, min_score: float = 0.65) -> List[Dict[str, Any]]:
    """Retrieve results using global retriever."""
    return get_retriever().retrieve(query_text, chat_id, top_k=top_k, modality_filter=modality_filter, min_score=min_score)
