import pdfplumber
import docx as python_docx
from pathlib import Path
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks, preferring sentence boundaries."""
    chunks = []
    text = text.strip()
    if not text:
        return []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        if end < len(text):
            boundary = text.rfind('. ', start, end)
            if boundary != -1 and boundary > start + 50:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break
    return chunks


def ingest_pdf(file_path: Path) -> list[dict]:
    results = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            if not raw_text.strip():
                continue
            for i, chunk in enumerate(chunk_text(raw_text)):
                results.append({
                    "page": page_num,
                    "chunk_index": i,
                    "text": chunk,
                    "modality": "pdf",
                    "start_time": None,
                    "end_time": None,
                    "image_path": None,
                })
    return results


def ingest_docx(file_path: Path) -> list[dict]:
    doc = python_docx.Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [
        {
            "page": 1,
            "chunk_index": i,
            "text": chunk,
            "modality": "docx",
            "start_time": None,
            "end_time": None,
            "image_path": None,
        }
        for i, chunk in enumerate(chunk_text(full_text))
    ]
