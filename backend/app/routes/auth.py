from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from ..users import User
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import os
import shutil
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    try:
        result = await User.create_user(user.email, user.password, user.full_name)
        if not result:
            raise HTTPException(status_code=400, detail="Email already registered")
        return {"id": str(result["_id"]), "email": result["email"]}
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_by_email(form_data.username)
    if not user or not User.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Ensure config loading or default is handled in auth.py
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Prepare user data
    user_data = {k: v for k, v in user.items() if k != "hashed_password"}
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
        
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_data
    }

@router.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    # Convert ObjectId to str for JSON serialization
    if "_id" in current_user:
        current_user["_id"] = str(current_user["_id"])
    return current_user

@router.put("/profile")
async def update_profile(user_update: UserUpdate, current_user = Depends(get_current_user)):
    try:
        email = current_user["email"]
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        
        if not update_data:
            return current_user

        success = await User.update_user(email, update_data)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update profile")
            
        # Refetch updated user
        updated_user = await User.get_by_email(email)
        if "_id" in updated_user:
            updated_user["_id"] = str(updated_user["_id"])
        
        # Remove password
        if "hashed_password" in updated_user:
            del updated_user["hashed_password"]
            
        return updated_user
    except Exception as e:
        print(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    try:
        email = current_user["email"]
        
        # Ensure uploads directory exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        storage_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "storage", "avatars"))
        os.makedirs(storage_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(storage_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update user avatar URL
        # URL should be relative path served by static
        avatar_url = f"/static/avatars/{filename}"
        
        success = await User.update_user(email, {"avatar_url": avatar_url})
        if not success:
             raise HTTPException(status_code=400, detail="Failed to update user avatar")
             
        return {"avatar_url": avatar_url}
        
    except Exception as e:
        print(f"Avatar upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
