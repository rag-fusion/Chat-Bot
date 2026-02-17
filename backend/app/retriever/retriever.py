"""
Enhanced retrieval with reranking, session isolation, and NTRO safeguards.
"""

from __future__ import annotations

import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from ..embeddings import embed_text
from ..vector_store import get_store


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
            return []

        # 1. Generate query embedding
        query_embedding = embed_text(query_text)
        
        # 2. Normalize Query (Store.search also does this, but good to be explicit/safe)
        # Note: faiss key in store handles normalization, so strict double norm is fine but redundant.
        # We rely on store.search to handle it correctly.
        
        # 3. Search in Session Index
        # Fetch more candidates for filtering/reranking
        search_k = min(top_k * 5, 100) 
        
        try:
            results = self.store.search(query_embedding, search_k, session_id=chat_id)
        except Exception as e:
            # Handle case where session index doesn't exist yet
            print(f"Search warning for session {chat_id}: {e}")
            return []
        
        # 4. Filter by Modality
        if modality_filter:
            results = [r for r in results if r.get('modality') == modality_filter]
        
        # 5. Filter by Score Threshold (NTRO Requirement)
        # IndexFlatIP with normalized vectors = Cosine Similarity (-1 to 1)
        filtered = [r for r in results if r.get('score', 0) >= min_score]
        
        if not filtered:
            return []
        
        # 6. Rerank Results
        reranked = self.rerank_results(query_text, filtered)
        
        return reranked[:top_k]
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using multiple signals."""
        if not results:
            return results
        
        for result in results:
            score = result.get('score', 0.0)
            
            # Boost score for exact matches
            content = (result.get('page_content') or result.get('content', '')).lower()
            query_lower = query.lower()
            if query_lower in content:
                score += 0.1
            
            # Boost score for title matches
            file_name = result.get('file_name', '').lower()
            if any(word in file_name for word in query_lower.split()):
                score += 0.05
            
            # Boost score for images (often high value)
            if result.get('modality') == 'image':
                score += 0.03
            
            result['rerank_score'] = score
        
        # Sort by rerank score
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
