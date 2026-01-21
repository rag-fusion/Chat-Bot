from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, upload, files, auth, history
from .database import connect_to_mongo, close_mongo_connection
from .rag import answer_query
from .chat_history import ChatHistory
from .auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
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

# Event Handlers
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None

@app.post("/query")
async def query_endpoint(request: QueryRequest, current_user = Depends(get_current_user)):
    try:
        # Resolve config path
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
        
        # Get Answer
        response = answer_query(cfg_path, request.query)
        
        # Save to history if chat_id provided
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

@app.get("/")
async def root():
    return {"message": "Offline RAG Backend Running", "docs_url": "/docs"}

# Ensure storage directories exist
try:
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "storage", "uploads"), exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create storage directory: {e}")
