"""
FAISS vector store wrapper with enhanced persistence.
"""

from .faiss_store import FAISSStore, get_store, upsert, search, persist, load

__all__ = [
    "FAISSStore",
    "get_store",
    "upsert",
    "search", 
    "persist",
    "load"
]
