from datetime import datetime
from bson import ObjectId
from typing import List
from .database import db

class ChatHistory:
    @staticmethod
    async def create_chat(user_id: str, title: str = "New Chat"):
        if db.db is None: raise Exception("Database not connected")
        
        chat_doc = {
            "user_id": ObjectId(user_id),
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        result = await db.db.chats.insert_one(chat_doc)
        chat_doc["_id"] = str(result.inserted_id)
        chat_doc["user_id"] = str(chat_doc["user_id"])
        return chat_doc

    @staticmethod
    async def get_user_chats(user_id: str):
        if db.db is None: return []
        cursor = db.db.chats.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1)
        chats = []
        async for chat in cursor:
            chat["_id"] = str(chat["_id"])
            chat["user_id"] = str(chat["user_id"])
            # Don't send all messages in list view
            if "messages" in chat:
                del chat["messages"]
            chats.append(chat)
        return chats

    @staticmethod
    async def get_chat(chat_id: str, user_id: str):
        if db.db is None: return None
        try:
           chat = await db.db.chats.find_one({
               "_id": ObjectId(chat_id), 
               "user_id": ObjectId(user_id)
           })
           if chat:
               chat["_id"] = str(chat["_id"])
               chat["user_id"] = str(chat["user_id"])
           return chat
        except:
            return None

    @staticmethod
    async def add_message(chat_id: str, role: str, content: str, sources: List[dict] = None):
        if db.db is None: return None
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        if sources:
            message["sources"] = sources

        await db.db.chats.update_one(
            {"_id": ObjectId(chat_id)},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return message
        
    @staticmethod
    async def update_title(chat_id: str, title: str):
        if db.db is None: return None
        await db.db.chats.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"title": title}}
        )
