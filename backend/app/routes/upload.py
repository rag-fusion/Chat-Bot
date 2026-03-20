import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..ingest import process_and_ingest_file

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    chat_id: str = Form(...)
):
    try:
        if not chat_id:
             raise HTTPException(status_code=400, detail="chat_id is required")

        logger.info(f"[UPLOAD ROUTE] chat_id={chat_id} file={file.filename}")

        # Pass chat_id as session_id — files are stored per session
        result = await process_and_ingest_file(file, session_id=chat_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
