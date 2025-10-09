"""
Embedding generation for multimodal content.
"""

from .generate import embed_text, embed_image, embed_audio_segment, get_text_model, get_clip

__all__ = [
    "embed_text",
    "embed_image", 
    "embed_audio_segment",
    "get_text_model",
    "get_clip"
]
