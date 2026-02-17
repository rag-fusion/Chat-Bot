"""
FAISS vector store wrapper with enhanced persistence.
"""

from .faiss_store import FAISSStore, get_store

__all__ = [
    "FAISSStore",
    "get_store"
]
