"""
Image processing and OCR capabilities.
"""

from __future__ import annotations

import os
from typing import List, Optional
from PIL import Image
from .base import Chunk
from ..image_utils import get_image_size


def detect_text_in_image(path: str) -> str:
    """Extract text from image using OCR (optional pytesseract)."""
    try:
        import pytesseract
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except ImportError:
        # pytesseract not available, return empty
        return ""
    except Exception:
        return ""


def image_to_embedding(path: str, file_name: str) -> List[Chunk]:
    """Process image and create chunk for embedding."""
    try:
        w, h = get_image_size(path)
    except Exception:
        w, h = None, None
    
    # Try OCR if available
    ocr_text = detect_text_in_image(path)
    
    ch = Chunk(
        content=f"Image: {file_name}" + (f" | OCR: {ocr_text}" if ocr_text else ""),
        file_name=file_name, 
        file_type="image", 
        filepath=path,
        width=w,
        height=h
    )
    return [ch]
