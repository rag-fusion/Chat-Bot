from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..utils.file_server import get_file_path
import os

router = APIRouter()

@router.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    """Serve uploaded files."""
    try:
        full_path = get_file_path(file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(full_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))