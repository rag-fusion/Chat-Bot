from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..ingest import process_and_ingest_file
import os

router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    chat_id: str = Form(...)
):
    try:
        if not chat_id:
             raise HTTPException(status_code=400, detail="chat_id is required")

        # Define storage directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path: backend/app/routes/../../storage/uploads -> backend/storage/uploads
        storage_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "storage", "uploads"))
        os.makedirs(storage_dir, exist_ok=True)
        
        # Pass chat_id as session_id
        result = await process_and_ingest_file(file, storage_dir, session_id=chat_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
