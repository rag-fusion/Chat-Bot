"""
Image processing and OCR capabilities.
"""

from __future__ import annotations

import os
import logging
from typing import List, Optional
from PIL import Image
from .base import Chunk
from ..image_utils import get_image_size

logger = logging.getLogger(__name__)


def detect_text_in_image(path: str) -> str:
    """Extract text from image using OCR (optional pytesseract).
    
    Returns:
        Extracted text string, or empty string if OCR is not available or fails.
    """
    try:
        import pytesseract
        logger.debug(f"Attempting OCR on image: {path}")
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        extracted = text.strip()
        if extracted:
            logger.debug(f"Successfully extracted {len(extracted)} characters via OCR")
        return extracted
    except ImportError:
        # pytesseract not available - use fallback description
        logger.debug("pytesseract not available. Using filename-based description.")
        return ""
    except Exception as e:
        # Log but don't fail - continue processing without OCR
        logger.warning(f"OCR extraction failed for {path}: {e}")
        return ""


def image_to_embedding(path: str, file_name: str) -> List[Chunk]:
    """Process image and create chunk for embedding with rich content.
    
    The chunk content includes:
    1. Image filename (always)
    2. OCR text if available (extracted via Tesseract)
    3. A semantic description hint
    
    This ensures that both visual (via CLIP embedding) and textual (via OCR) 
    aspects of the image are indexed and retrievable.
    """
    try:
        w, h = get_image_size(path)
    except Exception as e:
        logger.warning(f"Could not get image dimensions for {path}: {e}")
        w, h = None, None
    
    # Extract OCR text from image (if pytesseract available)
    ocr_text = detect_text_in_image(path)
    
    # Build rich content description for the image chunk
    content_parts = [f"Image: {file_name}"]
    
    # Add OCR text as primary content if available
    if ocr_text:
        content_parts.append(f"OCR Text: {ocr_text}")
    else:
        # Add dimensional hints for retrieval if no OCR
        if w and h:
            content_parts.append(f"Dimensions: {w}x{h} pixels")
    
    # Combine content - this will be embedded by CLIP (image embedding)
    # and also used for text search in vector store
    full_content = " | ".join(content_parts)
    
    ch = Chunk(
        content=full_content,
        file_name=file_name, 
        file_type="image", 
        filepath=path,
        width=w,
        height=h
    )
    return [ch]
