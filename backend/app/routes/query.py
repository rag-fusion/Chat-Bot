from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.rag_engine import ask

router = APIRouter()

class QueryRequest(BaseModel):
    chat_id: str
    question: str

@router.post("/query")
async def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty.")
    if not req.chat_id.strip():
        raise HTTPException(400, "chat_id is required.")
    return ask(req.chat_id, req.question)
