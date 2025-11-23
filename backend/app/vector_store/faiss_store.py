"""
Enhanced FAISS vector store with proper persistence and metadata handling.
"""

from __future__ import annotations

import os
import json
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
import faiss
import numpy as np


class FAISSStore:
    """Enhanced FAISS vector store with metadata persistence."""
    
    def __init__(self, dimension: int = 512, storage_dir: str = None):
        self.dimension = dimension
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "..", "..", "storage")
        self.index_path = os.path.join(self.storage_dir, "faiss.index")
        self.metadata_path = os.path.join(self.storage_dir, "metadata.json")
        self.db_path = os.path.join(self.storage_dir, "metadata.db")
        self.index = None
        self.metadata = {}
        self._ensure_storage()
        self._load_or_init()
    
    def _ensure_storage(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _load_or_init(self):
        """Load existing index or create new one with dimension migration support."""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                loaded_dim = self.index.d
                self._load_metadata()
                
                # Check if dimension mismatch (old 384-dim index)
                if loaded_dim != self.dimension:
                    print(f"Warning: Existing index has dimension {loaded_dim}, but expected {self.dimension}.")
                    print("The index will be migrated. Old index backed up to faiss.index.backup")
                    # Backup old index
                    import shutil
                    backup_path = self.index_path + ".backup"
                    if not os.path.exists(backup_path):
                        shutil.copy2(self.index_path, backup_path)
                    # Create new index with correct dimension
                    self.index = faiss.IndexFlatIP(self.dimension)
                    # Note: Old vectors cannot be migrated automatically - they need re-indexing
                    print("Please re-index your documents to migrate to the new dimension.")
                    print("Or run: python backend/scripts/migrate_to_clip.py")
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = {}
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = {}
    
    def _load_metadata(self):
        """Load metadata from JSON file."""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def upsert(self, items: List[Dict[str, Any]]) -> int:
        """Upsert items with embeddings and metadata."""
        if not items:
            return 0
        
        embeddings = []
        metadatas = []
        
        for item in items:
            embedding = item.get('embedding')
            if embedding is None:
                continue
            
            # Validate embedding dimension
            if isinstance(embedding, np.ndarray):
                if embedding.ndim == 1:
                    if embedding.shape[0] != self.dimension:
                        raise ValueError(
                            f"Embedding dimension mismatch: got {embedding.shape[0]}, "
                            f"expected {self.dimension}. Ensure all embeddings use CLIP (512-dim)."
                        )
                elif embedding.ndim == 2:
                    if embedding.shape[1] != self.dimension:
                        raise ValueError(
                            f"Embedding dimension mismatch: got {embedding.shape[1]}, "
                            f"expected {self.dimension}."
                        )
                    # Flatten batch dimension - take first element
                    embedding = embedding[0]
            
            embeddings.append(embedding)
            metadatas.append(item.get('metadata', {}))
        
        if not embeddings:
            return 0
        
        embeddings_array = np.array(embeddings).astype(np.float32)
        start_id = self.index.ntotal
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store metadata
        for i, metadata in enumerate(metadatas):
            vector_id = start_id + i
            self.metadata[str(vector_id)] = {
                'vector_id': vector_id,
                'page_content': metadata.get('page_content', ''),
                'file_name': metadata.get('file_name', ''),
                'file_type': metadata.get('file_type', ''),
                'page_number': metadata.get('page_number'),
                'timestamp': metadata.get('timestamp'),
                'start_ts': metadata.get('start_ts'),
                'end_ts': metadata.get('end_ts'),
                'filepath': metadata.get('filepath'),
                'width': metadata.get('width'),
                'height': metadata.get('height'),
                'bbox': metadata.get('bbox'),
                'char_start': metadata.get('char_start'),
                'char_end': metadata.get('char_end'),
                'modality': metadata.get('modality', 'text')
            }
        
        self._save_metadata()
        self._persist_index()
        return len(embeddings)
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors. Optimized for performance."""
        if self.index.ntotal == 0:
            return []
        
        # Optimize: ensure correct dtype and shape upfront
        query_embedding = np.ascontiguousarray(query_embedding.astype(np.float32))
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Limit search to available vectors
        search_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, search_k)
        
        # Optimize: pre-allocate results list and batch metadata lookup
        results = []
        metadata_keys = [str(idx) for idx in indices[0] if idx != -1]
        
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            # Fast metadata lookup
            metadata = self.metadata.get(str(idx), {})
            result = {
                'vector_id': idx,
                'score': float(score),
                **metadata
            }
            results.append(result)
        
        return results
    
    def _persist_index(self):
        """Save FAISS index to disk."""
        faiss.write_index(self.index, self.index_path)
    
    def persist(self, path: str = None):
        """Persist the entire store to disk."""
        if path:
            # Save to custom location
            faiss.write_index(self.index, path)
            metadata_path = path.replace('.index', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        else:
            # Save to default location
            self._persist_index()
            self._save_metadata()
    
    def load(self, path: str = None):
        """Load store from disk."""
        if path:
            self.index = faiss.read_index(path)
            metadata_path = path.replace('.index', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
        else:
            self._load_or_init()
    
    def status(self) -> Dict[str, Any]:
        """Get store status information."""
        return {
            'vectors': self.index.ntotal,
            'dimension': self.dimension,
            'files': len(set(meta.get('file_name', '') for meta in self.metadata.values())),
            'modalities': list(set(meta.get('modality', 'text') for meta in self.metadata.values()))
        }
    
    def rebuild_from_metadata(self):
        """Rebuild index from stored metadata (for dimension changes)."""
        if not self.metadata:
            return
        
        # This would require re-computing embeddings from original content
        # For now, just reinitialize with current dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Get all embeddings and IDs from metadata
        embeddings = []
        ids = []
        for vector_id, meta in self.metadata.items():
            # Assuming 'page_content' holds the text for embedding
            text_to_embed = meta.get('page_content', '')
            if text_to_embed:
                # Re-create embedding. This requires access to an embedding function.
                # This is a placeholder for where you'd call your embedding function.
                # from ..embeddings import embed_text
                # embedding = embed_text(text_to_embed)
                # embeddings.append(embedding)
                # ids.append(int(vector_id))
                pass  # Placeholder for re-embedding logic
    
        # if embeddings:
        #     self.index.add_with_ids(np.array(embeddings), np.array(ids))
        
        self._persist_index()

# Global store instance for backward compatibility
_store_instance: Optional[FAISSStore] = None


def get_store() -> FAISSStore:
    """Get global store instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = FAISSStore()
    return _store_instance


def upsert(items: List[Dict[str, Any]]) -> int:
    """Upsert items to global store."""
    return get_store().upsert(items)


def search(query_embedding: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
    """Search global store."""
    return get_store().search(query_embedding, top_k)


def persist(path: str = None):
    """Persist global store."""
    get_store().persist(path)


def load(path: str = None):
    """Load global store."""
    get_store().load(path)
