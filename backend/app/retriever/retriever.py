"""
Enhanced retrieval with reranking capabilities.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Any, Optional
from ..embeddings import embed_text
from ..vector_store import get_store


class Retriever:
    """Enhanced retriever with reranking capabilities."""
    
    def __init__(self, store=None):
        self.store = store or get_store()
    
    def retrieve(self, query_text: str, top_k: int = 10, modality_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve and rerank results for a query."""
        # Generate query embedding
        query_embedding = embed_text(query_text)
        
        # Search with higher k for reranking
        search_k = min(top_k * 3, self.store.index.ntotal)
        results = self.store.search(query_embedding, search_k)
        
        # Filter by modality if specified
        if modality_filter:
            results = [r for r in results if r.get('modality') == modality_filter]
        
        # Rerank results
        reranked = self.rerank_results(query_text, results)
        
        # Return top k
        return reranked[:top_k]
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using multiple signals."""
        if not results:
            return results
        
        # Simple reranking based on multiple factors
        for result in results:
            score = result.get('score', 0.0)
            
            # Boost score for exact matches in content
            content = result.get('content', '').lower()
            query_lower = query.lower()
            if query_lower in content:
                score += 0.1
            
            # Boost score for title/filename matches
            file_name = result.get('file_name', '').lower()
            if any(word in file_name for word in query_lower.split()):
                score += 0.05
            
            # Boost score for recent content (if timestamp available)
            timestamp = result.get('timestamp')
            if timestamp:
                score += 0.02
            
            # Boost score for specific modalities
            modality = result.get('modality', 'text')
            if modality == 'image':
                score += 0.03  # Images often contain important information
            
            result['rerank_score'] = score
        
        # Sort by rerank score
        results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        return results
    
    def retrieve_cross_modal(self, query_text: str, top_k: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve results grouped by modality."""
        all_results = self.retrieve(query_text, top_k * 2)
        
        # Group by modality
        grouped = {}
        for result in all_results:
            modality = result.get('modality', 'text')
            if modality not in grouped:
                grouped[modality] = []
            grouped[modality].append(result)
        
        # Limit each modality
        for modality in grouped:
            grouped[modality] = grouped[modality][:top_k]
        
        return grouped
    
    def find_similar_across_modalities(self, result: Dict[str, Any], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find similar content across different modalities."""
        content = result.get('content', '')
        if not content:
            return []
        
        # Generate embedding for the content
        content_embedding = embed_text(content)
        
        # Search for similar content
        similar = self.store.search(content_embedding, top_k=20)
        
        # Filter by threshold and different modalities
        filtered = []
        original_modality = result.get('modality', 'text')
        
        for sim_result in similar:
            if (sim_result.get('score', 0) >= threshold and 
                sim_result.get('modality') != original_modality and
                sim_result.get('vector_id') != result.get('vector_id')):
                filtered.append(sim_result)
        
        return filtered


# Global retriever instance
_retriever_instance: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """Get global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance


def retrieve(query_text: str, top_k: int = 10, modality_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve results using global retriever."""
    return get_retriever().retrieve(query_text, top_k, modality_filter)


def rerank_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rerank results using global retriever."""
    return get_retriever().rerank_results(query, results)
