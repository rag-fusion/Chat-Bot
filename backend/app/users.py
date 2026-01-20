from .database import db
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    async def get_by_email(email: str):
        if db.db is None: return None
        return await db.db.users.find_one({"email": email})

    @staticmethod
    async def create_user(email: str, password: str, full_name: str = None):
        if db.db is None: raise Exception("Database not connected")
        
        existing = await User.get_by_email(email)
        if existing:
            return None
            
        hashed_pw = User.get_password_hash(password)
        user_doc = {
            "email": email,
            "hashed_password": hashed_pw,
            "full_name": full_name,
            "created_at": datetime.utcnow()
        }
        
        result = await db.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return user_doc
