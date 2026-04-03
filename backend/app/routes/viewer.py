from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.vector_store.faiss_store import get_store
from app.config import get_files_dir

router = APIRouter()


@router.get("/viewer/{chat_id}/{vector_id}")
async def get_chunk_source(chat_id: str, vector_id: int):
    """Returns full metadata for a vector so frontend knows which viewer to open."""
    store = get_store(chat_id)
    meta  = store.get_by_id(vector_id)
    if not meta:
        raise HTTPException(404, f"vector_id {vector_id} not found in chat {chat_id}")
    return meta


@router.get("/file/{chat_id}/{filename}")
async def serve_file(chat_id: str, filename: str):
    """
    Serves the original uploaded file.
    The file is stored as {file_id}_{filename} — we search by original filename.
    """
    files_dir = get_files_dir(chat_id)
    matches   = list(files_dir.glob(f"*_{filename}"))
    if not matches:
        raise HTTPException(404, f"File '{filename}' not found in session '{chat_id}'")
    return FileResponse(
        matches[0],
        headers={"Cache-Control": "no-store"},
    )
