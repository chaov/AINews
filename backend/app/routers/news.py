from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.core.database import get_database
from app.models.news import NewsResponse, NewsCreate, NewsUpdate

router = APIRouter(prefix="/api/v1/news", tags=["news"])


def news_to_response(news_doc: dict) -> NewsResponse:
    return NewsResponse(
        id=str(news_doc["_id"]),
        title=news_doc["title"],
        summary=news_doc.get("summary"),
        evaluation=news_doc.get("evaluation"),
        source_name=news_doc["source_name"],
        source_url=news_doc["source_url"],
        category=news_doc["category"],
        tags=news_doc.get("tags", []),
        published_at=news_doc["published_at"],
        view_count=news_doc.get("view_count", 0),
        is_active=news_doc.get("is_active", True),
    )


@router.get("", response_model=List[NewsResponse])
async def get_news_list(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query = {"is_active": True}
    if category:
        query["category"] = category

    skip = (page - 1) * page_size
    cursor = db.news.find(query).sort("published_at", -1).skip(skip).limit(page_size)
    news_list = await cursor.to_list(length=page_size)

    return [news_to_response(news) for news in news_list]


@router.get("/search", response_model=List[NewsResponse])
async def search_news(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query = {
        "is_active": True,
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"summary": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ],
    }

    skip = (page - 1) * page_size
    cursor = db.news.find(query).sort("published_at", -1).skip(skip).limit(page_size)
    news_list = await cursor.to_list(length=page_size)

    return [news_to_response(news) for news in news_list]


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(news_id: str):
    db = get_database()
    if not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid news ID")

    news = await db.news.find_one({"_id": ObjectId(news_id)})
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    await db.news.update_one(
        {"_id": ObjectId(news_id)}, {"$inc": {"view_count": 1}}
    )

    return news_to_response(news)


@router.post("", response_model=NewsResponse)
async def create_news(news: NewsCreate):
    db = get_database()
    news_dict = news.model_dump()
    news_dict["created_at"] = datetime.now(timezone.utc)
    news_dict["updated_at"] = datetime.now(timezone.utc)
    news_dict["view_count"] = 0

    result = await db.news.insert_one(news_dict)
    created_news = await db.news.find_one({"_id": result.inserted_id})

    return news_to_response(created_news)


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(news_id: str, news: NewsUpdate):
    db = get_database()
    if not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid news ID")

    update_data = {k: v for k, v in news.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.news.update_one({"_id": ObjectId(news_id)}, {"$set": update_data})
    updated_news = await db.news.find_one({"_id": ObjectId(news_id)})

    if not updated_news:
        raise HTTPException(status_code=404, detail="News not found")

    return news_to_response(updated_news)


@router.delete("/{news_id}")
async def delete_news(news_id: str):
    db = get_database()
    if not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid news ID")

    result = await db.news.delete_one({"_id": ObjectId(news_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News not found")

    return {"message": "News deleted successfully"}
