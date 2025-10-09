"""
Document extraction for PDF and DOCX files.
"""

from __future__ import annotations

import fitz  # PyMuPDF
from docx import Document
from typing import List, Tuple
from .base import Chunk, _split_text


def extract_text_from_pdf(path: str, file_name: str) -> List[Chunk]:
    """Extract text from PDF with page-level chunking."""
    doc = fitz.open(path)
    chunks: List[Chunk] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
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
