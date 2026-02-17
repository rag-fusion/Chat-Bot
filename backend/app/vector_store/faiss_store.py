"""
Enhanced FAISS vector store with session isolation, proper persistence, and NTRO-level safeguards.
"""

from __future__ import annotations

import os
import json
import shutil
from typing import Dict, List, Optional, Any, Tuple
import faiss
import numpy as np

# Global cache for active session stores to avoid constant disk I/O
# session_id -> {index: faiss.Index, metadata: dict}
_active_sessions: Dict[str, Dict[str, Any]] = {}

class FAISSStore:
    """Session-isolated FAISS vector store with enhanced safeguards."""
    
    def __init__(self, dimension: int = 512, storage_dir: str = None):
        self.dimension = dimension
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "..", "..", "storage")
        self.sessions_dir = os.path.join(self.storage_dir, "sessions")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists."""
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def _get_session_paths(self, session_id: str) -> Tuple[str, str]:
        """Get paths for session index and metadata."""
        session_dir = os.path.join(self.sessions_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return (
            os.path.join(session_dir, "index.faiss"),
            os.path.join(session_dir, "metadata.json")
        )

    def _load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session index and metadata, or create new."""
        # Return cached if available
        if session_id in _active_sessions:
            return _active_sessions[session_id]

        index_path, metadata_path = self._get_session_paths(session_id)
        
        # Load or create index
        if os.path.exists(index_path):
            try:
                index = faiss.read_index(index_path)
                # Verify dimension
                if index.d != self.dimension:
                    print(f"Warning: Session {session_id} index dimension mismatch ({index.d} vs {self.dimension}). Resetting.")
                    index = self._create_new_index()
            except Exception as e:
                print(f"Error loading index for session {session_id}: {e}. Creating new.")
                index = self._create_new_index()
        else:
            index = self._create_new_index()

        # Load or create metadata
        metadata = {}
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Error loading metadata for session {session_id}: {e}. Resetting.")
                metadata = {}

        session_data = {"index": index, "metadata": metadata}
        _active_sessions[session_id] = session_data
        return session_data

    def _create_new_index(self) -> faiss.Index:
        """Create a new IndexIDMap2 wrapped IndexFlatIP."""
        # IndexFlatIP uses Inner Product (Cosine Similarity if normalized)
        quantizer = faiss.IndexFlatIP(self.dimension)
        # IndexIDMap2 enables add_with_ids
        return faiss.IndexIDMap2(quantizer)

    def _save_session(self, session_id: str):
        """Save session index and metadata to disk."""
        if session_id not in _active_sessions:
            return

        session_data = _active_sessions[session_id]
        index_path, metadata_path = self._get_session_paths(session_id)
        
        # Save index
        faiss.write_index(session_data["index"], index_path)
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(session_data["metadata"], f, indent=2, ensure_ascii=False)

    def upsert(self, items: List[Dict[str, Any]], session_id: str) -> int:
        """Upsert items with embedding normalization using add_with_ids."""
        if not items or not session_id:
            return 0
        
        session_data = self._load_session(session_id)
        index = session_data["index"]
        metadata_store = session_data["metadata"]
        
        embeddings = []
        ids = []
        new_metadatas = []
        
        # Determine start ID (simple auto-increment based on dict size / max key)
        # Using max integer key to ensure uniqueness even if some deleted
        start_id = 0
        if metadata_store:
            try:
                # Keys are stored as strings in JSON, need conversion
                int_keys = [int(k) for k in metadata_store.keys()]
                if int_keys:
                    start_id = max(int_keys) + 1
            except:
                start_id = len(metadata_store)

        for i, item in enumerate(items):
            embedding = item.get('embedding')
            if embedding is None:
                continue
            
            # 1. Validate Dimension
            embedding = np.array(embedding, dtype=np.float32)
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            
            if embedding.shape[1] != self.dimension:
                print(f"Skipping embedding with wrong dimension: {embedding.shape}")
                continue
            
            # 2. Normalize Embedding (L2) - Vital for Cosine Similarity with IndexFlatIP
            faiss.normalize_L2(embedding)
            
            vector_id = start_id + i
            embeddings.append(embedding[0]) # Flatten for list
            ids.append(vector_id)
            
            # Prepare metadata
            meta = item.get('metadata', {})
            new_metadatas.append({
                'vector_id': vector_id,
                'session_id': session_id,
                'page_content': meta.get('page_content') or meta.get('content', ''),
                'file_name': meta.get('file_name', ''),
                'file_type': meta.get('file_type', ''),
                'modality': meta.get('modality', 'text'), # Explicit modality
                'page_number': meta.get('page_number'),
                'timestamp': meta.get('timestamp'),
                'filepath': meta.get('filepath'),
                'width': meta.get('width'),
                'height': meta.get('height'),
                'bbox': meta.get('bbox')
            })

        if not embeddings:
            return 0
        
        # 3. Add to Index with IDs
        embeddings_array = np.array(embeddings).astype(np.float32)
        ids_array = np.array(ids).astype(np.int64)
        
        index.add_with_ids(embeddings_array, ids_array)
        
        # 4. Update Metadata
        for i, meta in enumerate(new_metadatas):
            vector_id = ids[i]
            metadata_store[str(vector_id)] = meta
            
        # 5. Persist Immediately
        self._save_session(session_id)
        
        return len(embeddings)

    def search(self, query_embedding: np.ndarray, top_k: int, session_id: str) -> List[Dict[str, Any]]:
        """Search in specific session index with normalization."""
        if not session_id:
            return []
            
        session_data = self._load_session(session_id)
        index = session_data["index"]
        metadata_store = session_data["metadata"]
        
        if index.ntotal == 0:
            return []
        
        # 1. Prepare Query
        query_embedding = np.ascontiguousarray(query_embedding.astype(np.float32))
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # 2. Normalize Query (L2)
        faiss.normalize_L2(query_embedding)
        
        # 3. Search
        search_k = min(top_k, index.ntotal)
        scores, indices = index.search(query_embedding, search_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            
            # 4. Retrieve Metadata by ID
            meta = metadata_store.get(str(idx))
            if meta:
                result = meta.copy()
                result['score'] = float(score)
                results.append(result)
                
        return results
    
    def get_metadata(self, session_id: str, vector_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve specific metadata for viewer."""
        session_data = self._load_session(session_id)
        return session_data["metadata"].get(str(vector_id))

    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """Retrieve all metadata for a session."""
        session_data = self._load_session(session_id)
        return session_data["metadata"]

# Global store instance for backward compatibility
_store_instance: Optional[FAISSStore] = None

def get_store() -> FAISSStore:
    """Get global store instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = FAISSStore()
    return _store_instance
