from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..chat_history import ChatHistory
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
async def get_history(current_user = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        chats = await ChatHistory.get_user_chats(user_id)
        return chats
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
