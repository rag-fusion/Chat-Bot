"""
Document extraction for PDF and DOCX files.
"""

from __future__ import annotations

import fitz  # PyMuPDF
from docx import Document
from typing import List, Tuple
from .base import Chunk, _split_text


def extract_text_from_pdf(path: str, file_name: str) -> List[Chunk]:
    """Extract text from PDF with page-level chunking and scanned PDF support."""
    # Import locally to avoid potential circular dependencies
    from .image_processor import image_to_embedding
    import os
    
    doc = fitz.open(path)
    chunks: List[Chunk] = []
    
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        cleaned_text = text.strip()
        
        if cleaned_text:
            # Normal text extraction
            page_chunks = _split_text(text)
            char_offset = 0
            for ch in page_chunks:
                chunks.append(Chunk(
                    content=ch, 
                    file_name=file_name, 
                    file_type="pdf", 
                    page_number=i, 
                    filepath=path,
                    char_start=char_offset,
                    char_end=char_offset + len(ch)
                ))
                char_offset += len(ch)
        else:
            # Fallback for Scanned PDF: Render page as image
            try:
                # Render at 2x zoom for better OCR/details
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Save extracted page image to storage
                safe_name = os.path.splitext(file_name)[0]
                page_img_name = f"{safe_name}_page_{i}.png"
                page_img_path = os.path.join(os.path.dirname(path), page_img_name)
                
                pix.save(page_img_path)
                
                # Process using image processor (CLIP embedding + OCR)
                img_chunks = image_to_embedding(page_img_path, f"{file_name} (Page {i})")
                
                for ch in img_chunks:
                    # Ensure it is treated as an image for embedding, but link to PDF page
                    ch.file_type = "image"  # ingest.py uses this to trigger CLIP embed_image
                    ch.page_number = i
                    ch.modality = "image"   # Explicitly set modality
                
                chunks.extend(img_chunks)
                
            except Exception as e:
                print(f"Warning: Failed to extract page {i} from {file_name} as image: {e}")
                
    doc.close()
    return chunks


def extract_text_from_docx(path: str, file_name: str) -> List[Chunk]:
    """Extract text from DOCX with paragraph-level chunking."""
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    chunks = []
    doc_chunks = _split_text(text)
    char_offset = 0
    for i, ch in enumerate(doc_chunks):
        chunks.append(Chunk(
            content=ch, 
            file_name=file_name, 
            file_type="docx", 
            filepath=path,
            char_start=char_offset,
            char_end=char_offset + len(ch)
        ))
        char_offset += len(ch)
    return chunks
