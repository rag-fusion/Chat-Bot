"""
Legacy embeddings module - DEPRECATED.

This module is kept for backward compatibility but now delegates to the new
CLIP-based embeddings in embeddings/generate.py.

All functions now use the unified 512-dim CLIP embedding space.
"""

from __future__ import annotations

from typing import List
import numpy as np

# Import from the new unified embeddings module (via __init__.py)
from .embeddings import embed_text, embed_image, get_text_model as _get_text_model, get_clip as _get_clip


def get_text_model():
    """Legacy function - now uses CLIP text encoder (512-dim)."""
    return _get_text_model()


def get_clip():
    """Legacy function - now uses CLIP model (512-dim)."""
    return _get_clip()


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Legacy function for backward compatibility.
    Now uses CLIP text encoder (512-dim) instead of sentence-transformers.
    """
    return embed_text(texts)


def embed_image_paths(paths: List[str]) -> np.ndarray:
    """
    Legacy function for backward compatibility.
    Uses CLIP image encoder (512-dim).
    """
    embeddings = []
    for path in paths:
        emb = embed_image(path)
        embeddings.append(emb[0])  # Remove batch dimension
    return np.array(embeddings)


