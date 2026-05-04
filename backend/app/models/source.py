from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str
    code: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryInDB(CategoryBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True


class CategoryResponse(BaseModel):
    id: str
    name: str
    code: str
    icon: Optional[str]
    sort_order: int


class NewsSourceBase(BaseModel):
    name: str
    url: str
    type: str
    config: Dict[str, Any] = {}
    is_active: bool = True


class NewsSourceCreate(NewsSourceBase):
    pass


class NewsSourceInDB(NewsSourceBase):
    id: str = Field(alias="_id")
    last_fetch_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class NewsSourceResponse(BaseModel):
    id: str
    name: str
    url: str
    type: str
    is_active: bool
    last_fetch_at: Optional[datetime]
