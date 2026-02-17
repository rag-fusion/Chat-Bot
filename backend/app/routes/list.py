from fastapi import APIRouter, HTTPException, Query
from ..vector_store import get_store
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter()

@router.get("/list")
async def list_uploaded_files(chat_id: str = Query(..., description="Session/Chat ID")):
    """List all uploaded files involved in the current session."""
    try:
        # Get vector store for metadata
        store = get_store()
        session_metadata = store.get_session_metadata(chat_id)
        
        # Aggregate files from metadata
        files_stats = {}
        
        for meta in session_metadata.values():
            file_name = meta.get('file_name')
            if not file_name:
                continue
                
            if file_name not in files_stats:
                files_stats[file_name] = {
                    "file_name": file_name,
                    "chunk_count": 0,
                    "modalities": set(),
                    "upload_date": meta.get("timestamp") or datetime.now().isoformat()
                }
            
            files_stats[file_name]["chunk_count"] += 1
            files_stats[file_name]["modalities"].add(meta.get('modality', 'text'))
            
        # Convert to list
        files_list = []
        for fname, stats in files_stats.items():
            stats["modalities"] = list(stats["modalities"])
            # File size is hard to get if we don't look at disk, but we can try looking at storage/uploads
            # Assuming files are still in storage/uploads for now
            current_dir = os.path.dirname(os.path.abspath(__file__))
            storage_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "storage", "uploads"))
            file_path = os.path.join(storage_dir, fname)
            if os.path.exists(file_path):
                stats["file_size"] = os.path.getsize(file_path)
            else:
                stats["file_size"] = 0
                
            files_list.append(stats)
        
        # Sort by upload date (newest first)
        files_list.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return {"files": files_list, "total": len(files_list)}
        
    except Exception as e:
        print(f"Error listing files: {e}")
        # Return empty list instead of error to avoid breaking UI if session is new
        return {"files": [], "total": 0}
