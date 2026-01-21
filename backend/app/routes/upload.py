from fastapi import APIRouter, UploadFile, File, HTTPException
from ..ingest import process_and_ingest_file
import os

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Define storage directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path: backend/app/routes/../../storage/uploads -> backend/storage/uploads
        storage_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "storage", "uploads"))
        os.makedirs(storage_dir, exist_ok=True)
        
        result = await process_and_ingest_file(file, storage_dir)
        return result
    except Exception as e:
        print(f"Error in upload endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
