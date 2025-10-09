"""
Base classes and utilities for ingestion.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Chunk:
    """Represents a chunk of content with metadata."""
    content: str
    file_name: str
    file_type: str
    page_number: Optional[int] = None
    timestamp: Optional[str] = None
    filepath: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bbox: Optional[str] = None


def _split_text(text: str, min_size: int = 200, max_size: int = 500, overlap_ratio: float = 0.2) -> List[str]:
    """Split text into overlapping chunks."""
    text = (text or "").strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    overlap = int(max_size * overlap_ratio)
    while start < len(text):
        end = min(start + max_size, len(text))
        # try to end at sentence boundary
        boundary = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
        if boundary != -1 and boundary + 1 - start >= min_size:
            end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def extract_any(path: str, file_name: str, mime: str) -> List[Chunk]:
    """Extract content from any supported file type."""
    lower = file_name.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(path, file_name)
    if lower.endswith(".docx"):
        return extract_text_from_docx(path, file_name)
    if lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
        return image_to_embedding(path, file_name)
    if lower.endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg')):
        return transcribe_audio(path, file_name)
    # Fallback: treat as plain text
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        chunks = []
        for i, ch in enumerate(_split_text(text)):
            chunks.append(Chunk(
                content=ch, 
                file_name=file_name, 
                file_type="text", 
                filepath=path,
                char_start=i * 200,
                char_end=(i + 1) * 200
            ))
        return chunks
    except Exception:
        return []


# Import functions to avoid circular imports
def extract_text_from_pdf(path: str, file_name: str) -> List[Chunk]:
    from .doc_extractor import extract_text_from_pdf as _extract
    return _extract(path, file_name)


def extract_text_from_docx(path: str, file_name: str) -> List[Chunk]:
    from .doc_extractor import extract_text_from_docx as _extract
    return _extract(path, file_name)


def image_to_embedding(path: str, file_name: str) -> List[Chunk]:
    from .image_processor import image_to_embedding as _extract
    return _extract(path, file_name)


def transcribe_audio(path: str, file_name: str) -> List[Chunk]:
    from .audio_transcriber import transcribe_audio as _extract
    return _extract(path, file_name)
