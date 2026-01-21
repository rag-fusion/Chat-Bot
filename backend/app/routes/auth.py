from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from ..users import User
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

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

@router.post("/login", response_model=Token)
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
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    # Convert ObjectId to str for JSON serialization
    if "_id" in current_user:
        current_user["_id"] = str(current_user["_id"])
    return current_user
