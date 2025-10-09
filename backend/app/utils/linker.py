"""
Cross-modal linking utilities.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, Tuple
import numpy as np
from ..embeddings import embed_text


class CrossModalLinker:
    """Links similar content across different modalities."""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def find_links(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find cross-modal links between results."""
        if len(results) < 2:
            return results
        
        # Group by modality
        modalities = {}
        for result in results:
            modality = result.get('modality', result.get('file_type', 'text'))
            if modality not in modalities:
                modalities[modality] = []
            modalities[modality].append(result)
        
        # Find links between different modalities
        linked_results = []
        processed_ids = set()
        
        for result in results:
            if result.get('vector_id') in processed_ids:
                continue
            
            linked_group = [result]
            processed_ids.add(result.get('vector_id'))
            
            # Find similar content in other modalities
            for other_modality, other_results in modalities.items():
                if other_modality == result.get('modality', result.get('file_type', 'text')):
                    continue
                
                for other_result in other_results:
                    if other_result.get('vector_id') in processed_ids:
                        continue
                    
                    similarity = self._compute_similarity(result, other_result)
                    if similarity >= self.similarity_threshold:
                        linked_group.append(other_result)
                        processed_ids.add(other_result.get('vector_id'))
            
            # Add cross-modal links to each result in the group
            for linked_result in linked_group:
                linked_result['cross_modal_links'] = [
                    r for r in linked_group if r != linked_result
                ]
                linked_result['link_confidence'] = len(linked_group) - 1
            
            linked_results.extend(linked_group)
        
        return linked_results
    
    def _compute_similarity(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> float:
        """Compute similarity between two results."""
        content1 = result1.get('content', '')
        content2 = result2.get('content', '')
        
        if not content1 or not content2:
            return 0.0
        
        # Use text embedding similarity
        try:
            emb1 = embed_text(content1)
            emb2 = embed_text(content2)
            
            # Compute cosine similarity
            similarity = np.dot(emb1[0], emb2[0]) / (np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0]))
            return float(similarity)
        except Exception:
            return 0.0


def find_cross_modal_links(results: List[Dict[str, Any]], 
                          similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Find cross-modal links between results."""
    linker = CrossModalLinker(similarity_threshold)
    return linker.find_links(results)


def create_citations(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create formatted citations from results."""
    citations = []
    
    for i, result in enumerate(results, start=1):
        citation = {
            'id': i,
            'file_name': result.get('file_name', 'Unknown'),
            'file_type': result.get('file_type', 'unknown'),
            'modality': result.get('modality', result.get('file_type', 'text')),
            'snippet': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', ''),
            'score': result.get('score', 0.0),
            'page_number': result.get('page_number'),
            'timestamp': result.get('timestamp'),
            'filepath': result.get('filepath'),
            'cross_modal_links': result.get('cross_modal_links', []),
            'link_confidence': result.get('link_confidence', 0)
        }
        citations.append(citation)
    
    return citations


def format_source_reference(result: Dict[str, Any], index: int) -> str:
    """Format a source reference for display."""
    file_name = result.get('file_name', 'Unknown')
    file_type = result.get('file_type', 'unknown')
    
    ref = f"[{index}] {file_name}"
    
    if file_type == 'pdf' and result.get('page_number'):
        ref += f", page {result['page_number']}"
    elif file_type == 'audio' and result.get('timestamp'):
        ref += f", {result['timestamp']}"
    elif file_type == 'image':
        ref += " (image)"
    
    return ref
