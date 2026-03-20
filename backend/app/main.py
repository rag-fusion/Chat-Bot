import logging
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

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

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
    
    logger.info("=" * 50)
    logger.info("Startup Check:")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ GPU detected: {gpu_name}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    else:
        logger.warning("⚠️ GPU NOT DETECTED. Running in CPU mode.")
    logger.info("=" * 50)
    
    # Indices are lazy-loaded per session — no global index to load.
    
    await connect_to_mongo()

app.add_event_handler("shutdown", close_mongo_connection)

class QueryRequest(BaseModel):
    query: str
    chat_id: str  # Required for session isolation
    session_files: Optional[List[str]] = None 

@app.post("/query")
async def query_endpoint(request: QueryRequest, current_user = Depends(get_current_user)):
    try:
        # Resolve config path
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
        
        if not request.chat_id:
             raise HTTPException(status_code=400, detail="chat_id is required")

        logger.info(f"[QUERY] chat_id={request.chat_id} query={request.query[:80]}...")

        # Get Answer with session context
        response = answer_query(
            cfg_path, 
            request.query, 
            chat_id=request.chat_id,
            session_files=request.session_files
        )
        
        logger.info(f"[QUERY] chat_id={request.chat_id} sources_returned={len(response.get('sources', []))}")

        # Save to history
        if request.chat_id:
            user_id = str(current_user["_id"])
            # Save user message
            await ChatHistory.add_message(request.chat_id, "user", request.query)
            # Save assistant message
            await ChatHistory.add_message(request.chat_id, "assistant", response["answer"], response.get("sources"))
            
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(list.router, prefix="/api/files", tags=["files"])
app.include_router(viewer.router, prefix="/api", tags=["viewer"])

@app.get("/")
async def root():
    return {"message": "Offline RAG Backend Running", "docs_url": "/docs"}

# Ensure session storage directory exists
try:
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "storage", "sessions"), exist_ok=True)
except Exception as e:
    logger.warning(f"Could not create storage directory: {e}")
