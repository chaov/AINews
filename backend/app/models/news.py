from datetime import datetime, timezone
from typing import Optional, List, Any
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def _validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class NewsBase(BaseModel):
    title: str
    summary: Optional[str] = None
    evaluation: Optional[str] = None
    content: Optional[str] = None
    source_name: str
    source_url: str
    category: str
    tags: List[str] = []
    published_at: datetime
    is_active: bool = True


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    evaluation: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NewsInDB(NewsBase):
    id: str = Field(alias="_id")
    view_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class NewsResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    evaluation: Optional[str]
    source_name: str
    source_url: str
    category: str
    tags: List[str]
    published_at: datetime
    view_count: int
    is_active: bool
