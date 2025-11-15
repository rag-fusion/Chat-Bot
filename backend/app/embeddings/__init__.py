"""
Embedding generation for multimodal content.
"""

from .generate import embed_text, embed_image, embed_audio_segment, get_text_model, get_clip, embed_texts, embed_image_paths

__all__ = [
    "embed_text",
    "embed_image", 
    "embed_audio_segment",
    "get_text_model",
    "get_clip",
    "embed_texts",  # Legacy function for backward compatibility
    "embed_image_paths"  # Legacy function for backward compatibility
]
