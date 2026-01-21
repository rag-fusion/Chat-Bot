from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..rag import answer_query
from ..auth import get_current_user
from ..chat_history import ChatHistory
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

class NewChatRequest(BaseModel):
    title: str

@router.post("/new")
async def create_chat(request: NewChatRequest, current_user = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        chat = await ChatHistory.create_chat(user_id, request.title)
        return chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}")
async def get_chat(chat_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        chat = await ChatHistory.get_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
