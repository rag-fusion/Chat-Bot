import logging
from fastapi import APIRouter, HTTPException, Path
from ..vector_store import get_store

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/viewer/{session_id}/{vector_id}")
async def get_citation_context(
    session_id: str = Path(..., description="The chat/session ID"),
    vector_id: int = Path(..., description="The vector ID of the citation")
):
    """
    Retrieve specific text chunk and metadata for a citation.
    Resolves via session_id + vector_id — never by file name alone.
    """
    try:
        logger.info(f"[VIEWER] session_id={session_id} vector_id={vector_id}")
        
        store = get_store()
        metadata = store.get_metadata(session_id, vector_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Citation not found")
            
        return {
            "session_id": session_id,
            "vector_id": vector_id,
            "text": metadata.get("page_content", ""),
            "file_name": metadata.get("file_name", ""),
            "page_number": metadata.get("page_number"),
            "modality": metadata.get("modality", "text"),
            "chunk_index": metadata.get("chunk_index"),
            "file_id": metadata.get("file_id", ""),
            "score": metadata.get("score"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VIEWER] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
