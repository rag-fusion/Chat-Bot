"""
Ingestion pipeline for multimodal documents.
Supports PDF, DOCX, images, and audio files.
"""

from .doc_extractor import extract_text_from_pdf, extract_text_from_docx
from .image_processor import detect_text_in_image, image_to_embedding
from .audio_transcriber import transcribe_audio
from .base import Chunk, extract_any

__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_docx", 
    "detect_text_in_image",
    "image_to_embedding",
    "transcribe_audio",
    "Chunk",
    "extract_any"
]
