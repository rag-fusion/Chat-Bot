from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, upload, files, auth, history, list, viewer
from .database import connect_to_mongo, close_mongo_connection
from .rag import answer_query
from .chat_history import ChatHistory
from .auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import os

app = FastAPI(title="Offline Multimodal RAG API")

# Setup CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
if not os.path.exists(storage_dir):
    try:
        os.makedirs(storage_dir)
    except Exception:
        pass
app.mount("/static", StaticFiles(directory=storage_dir), name="static")

# Event Handlers
@app.on_event("startup")
async def startup_event():
    import torch
    import logging
    logger = logging.getLogger("uvicorn")
    
    logger.info("=" * 50)
    logger.info("Startup Check:")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ GPU detected: {gpu_name}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    else:
        logger.warning("⚠️ GPU NOT DETECTED. Running in CPU mode.")
    logger.info("=" * 50)
    
    # No longer loading global index here! 
    # Indices are lazy-loaded per session.
    
    await connect_to_mongo()

app.add_event_handler("shutdown", close_mongo_connection)

class QueryRequest(BaseModel):
    query: str
    chat_id: str # Required now for session isolation
    session_files: Optional[List[str]] = None 

@app.post("/query")
async def query_endpoint(request: QueryRequest, current_user = Depends(get_current_user)):
    try:
        # Resolve config path
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
        
        if not request.chat_id:
             raise HTTPException(status_code=400, detail="chat_id is required")

        # Get Answer with session context
        response = answer_query(
            cfg_path, 
            request.query, 
            chat_id=request.chat_id,
            session_files=request.session_files
        )
        
        # Save to history
        if request.chat_id:
            user_id = str(current_user["_id"])
            # Save user message
            await ChatHistory.add_message(request.chat_id, "user", request.query)
            # Save assistant message
            await ChatHistory.add_message(request.chat_id, "assistant", response["answer"], response.get("sources"))
            
        return response
    except Exception as e:
        print(f"Query Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(list.router, prefix="/api/files", tags=["files"])
app.include_router(viewer.router, prefix="/api", tags=["viewer"]) # New viewer endpoint

@app.get("/")
async def root():
    return {"message": "Offline RAG Backend Running", "docs_url": "/docs"}

# Ensure storage directories exist
try:
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "storage", "uploads"), exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create storage directory: {e}")
