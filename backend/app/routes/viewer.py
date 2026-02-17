from fastapi import APIRouter, HTTPException, Path
from ..vector_store import get_store
import os

router = APIRouter()

@router.get("/viewer/{session_id}/{vector_id}")
async def get_citation_context(
    session_id: str = Path(..., description="The chat/session ID"),
    vector_id: int = Path(..., description="The vector ID of the citation")
):
    """
    Retrieve specific text chunk and metadata for a citation.
    Used by the frontend to show the exact source context.
    """
    try:
        store = get_store()
        metadata = store.get_metadata(session_id, vector_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Citation not found")
            
        return {
            "text": metadata.get("page_content", ""),
            "file_name": metadata.get("file_name", ""),
            "page_number": metadata.get("page_number"),
            "modality": metadata.get("modality", "text"),
            "score": metadata.get("score"), # Might not be stored in metadata persistence, but that's ok
            "file_path": metadata.get("filepath", "") # Internal use, maybe don't expose full path if sensitive?
            # Frontend can use file_name to request file via /api/files/ if needed
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
