"""
Enhanced embedding generation with proper offline support.
"""

from __future__ import annotations

import os
from typing import List, Union
import numpy as np
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
import open_clip


_text_model: SentenceTransformer | None = None
_clip_model: torch.nn.Module | None = None
_clip_preprocess = None


def get_text_model() -> SentenceTransformer:
    """Get or initialize text embedding model."""
    global _text_model
    if _text_model is None:
        # Try to load from local path first, fallback to model name
        local_path = os.getenv("TEXT_MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")
        if os.path.exists(local_path):
            _text_model = SentenceTransformer(local_path)
        else:
            _text_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _text_model


def get_clip() -> tuple[torch.nn.Module, any]:
    """Get or initialize CLIP model for image embeddings."""
    global _clip_model, _clip_preprocess
    if _clip_model is None:
        # Try to load from local path first
        local_path = os.getenv("CLIP_MODEL_PATH")
        if local_path and os.path.exists(local_path):
            # Load from local checkpoint
            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained=False
            )
            checkpoint = torch.load(local_path, map_location="cpu")
            model.load_state_dict(checkpoint)
        else:
            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="openai"
            )
        model.eval()
        _clip_model = model
        _clip_preprocess = preprocess
    return _clip_model, _clip_preprocess


def embed_text(text: Union[str, List[str]]) -> np.ndarray:
    """Generate embeddings for text."""
    model = get_text_model()
    if isinstance(text, str):
        text = [text]
    embs = model.encode(text, convert_to_numpy=True, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    return embs.astype(np.float32)


def embed_image(path: str) -> np.ndarray:
    """Generate embeddings for image."""
    model, preprocess = get_clip()
    image = preprocess(Image.open(path).convert("RGB"))
    batch = torch.stack([image])
    with torch.no_grad():
        feats = model.encode_image(batch)
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy().astype(np.float32)


def embed_audio_segment(transcript: str) -> np.ndarray:
    """Generate embeddings for audio transcript (uses text embedding)."""
    return embed_text(transcript)


# Legacy functions for backward compatibility
def embed_texts(texts: List[str]) -> np.ndarray:
    """Legacy function for backward compatibility."""
    return embed_text(texts)


def embed_image_paths(paths: List[str]) -> np.ndarray:
    """Legacy function for backward compatibility."""
    embeddings = []
    for path in paths:
        emb = embed_image(path)
        embeddings.append(emb[0])  # Remove batch dimension
    return np.array(embeddings)
