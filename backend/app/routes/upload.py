import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.config import get_files_dir, SUPPORTED_EXTENSIONS
from app.embedder.embedder import embed_texts
from app.vector_store.faiss_store import get_store
from app.ingestion.pdf_ingestor import ingest_pdf, ingest_docx
from app.ingestion.image_ingestor import ingest_image
from app.ingestion.audio_ingestor import ingest_audio

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chat_id: str = Form(...),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {list(SUPPORTED_EXTENSIONS.keys())}")

    modality = SUPPORTED_EXTENSIONS[ext]

    # Save original file
    files_dir = get_files_dir(chat_id)
    file_id   = str(uuid.uuid4())[:8]
    save_name = f"{file_id}_{file.filename}"
    save_path = files_dir / save_name

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract chunks based on file type
    try:
        if modality == "pdf":
            chunks = ingest_pdf(save_path)
        elif modality == "docx":
            chunks = ingest_docx(save_path)
        elif modality == "image":
            chunks = ingest_image(save_path)
        elif modality == "audio":
            chunks = ingest_audio(save_path)
        else:
            raise HTTPException(400, "Unknown modality")
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(422, f"Extraction failed: {str(e)}")

    if not chunks:
        raise HTTPException(422, "No content could be extracted from this file.")

    # Embed all chunk texts
    texts      = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    # Build metadata
    metadata_list = [{
        "chat_id":     chat_id,
        "file_id":     file_id,
        "file_name":   file.filename,
        "modality":    modality,
        "page":        c.get("page"),
        "chunk_index": c.get("chunk_index", 0),
        "text":        c["text"],
        "start_time":  c.get("start_time"),
        "end_time":    c.get("end_time"),
        "image_path":  c.get("image_path"),
        "saved_as":    save_name,
    } for c in chunks]

    # Add to FAISS
    store      = get_store(chat_id)
    vector_ids = store.add(embeddings, metadata_list)

    return {
        "status":          "success",
        "file_name":        file.filename,
        "file_id":          file_id,
        "modality":         modality,
        "chunks_indexed":   len(chunks),
        "vector_ids_start": vector_ids[0],
        "vector_ids_end":   vector_ids[-1],
    }
