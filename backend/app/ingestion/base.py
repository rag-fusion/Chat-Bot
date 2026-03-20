"""
Base classes and utilities for ingestion.
"""

from __future__ import annotations

import os
import re
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


# Patterns that indicate a heading or label line
_HEADING_RE = re.compile(
    r'^(?:'
    r'#{1,6}\s|'                           # Markdown headings
    r'[A-Z][A-Za-z\s]{2,40}:\s*$|'         # "Title:" style labels
    r'[A-Z][A-Z\s]{3,40}$|'               # ALL-CAPS headings
    r'\d+\.\s+[A-Z]|'                      # "1. Heading" numbered section
    r'(?:project|title|name|abstract|summary|problem|objective|introduction|conclusion)'  # common heading keywords
    r')',
    re.IGNORECASE | re.MULTILINE
)


def _split_text(text: str, min_size: int = 150, max_size: int = 600, overlap_ratio: float = 0.15) -> List[str]:
    """Split text into chunks that preserve heading+value pairs.
    
    Strategy:
    1. Split on paragraph boundaries (double newlines).
    2. If a paragraph looks like a heading, merge it with the next paragraph.
    3. Then enforce max_size with sentence-boundary splitting.
    """
    text = (text or "").strip()
    if not text:
        return []

    # Step 1: Split into paragraphs (double-newline or heading-pattern boundaries)
    paragraphs = re.split(r'\n{2,}', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # Step 2: Merge heading paragraphs with the paragraph that follows them
    merged: List[str] = []
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i]
        # Check if this paragraph is a heading (short + matches heading pattern)
        is_heading = (
            len(para) < 80
            and _HEADING_RE.search(para)
            and i + 1 < len(paragraphs)
        )
        if is_heading:
            # Merge heading with next paragraph
            merged.append(para + "\n" + paragraphs[i + 1])
            i += 2
        else:
            merged.append(para)
            i += 1

    # Step 3: Build final chunks respecting max_size
    chunks: List[str] = []
    overlap = int(max_size * overlap_ratio)

    for block in merged:
        if len(block) <= max_size:
            # Small enough — keep as-is
            if block:
                chunks.append(block)
        else:
            # Too large — split at sentence boundaries within the block
            start = 0
            while start < len(block):
                end = min(start + max_size, len(block))
                # Try to end at a sentence boundary
                boundary = max(
                    block.rfind(". ", start, end),
                    block.rfind(".\n", start, end),
                    block.rfind("\n", start, end)
                )
                if boundary != -1 and boundary + 1 - start >= min_size:
                    end = boundary + 1
                chunk = block[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                if end >= len(block):
                    break
                start = max(0, end - overlap)

    # Drop tiny fragments
    chunks = [c for c in chunks if len(c) >= 30]
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
