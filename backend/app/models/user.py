from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class UserBase(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class HistoryItem(BaseModel):
    news_id: str
    viewed_at: datetime


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    email: Optional[str] = None
    phone: Optional[str] = None
    hashed_password: str
    favorites: List[str] = []
    history: List[HistoryItem] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserResponse(BaseModel):
    id: str
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    favorites: List[str]
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
