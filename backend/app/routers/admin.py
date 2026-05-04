from typing import List
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.core.database import get_database
from app.models.source import CategoryResponse, CategoryCreate, NewsSourceResponse, NewsSourceCreate
from app.routers.user import get_current_user, get_admin_user

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
async def get_categories():
    db = get_database()
    cursor = db.categories.find({"is_active": True}).sort("sort_order", 1)
    categories = await cursor.to_list(length=100)

    return [
        CategoryResponse(
            id=str(c["_id"]),
            name=c["name"],
            code=c["code"],
            icon=c.get("icon"),
            sort_order=c.get("sort_order", 0),
        )
        for c in categories
    ]


@router.post("", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    user_id: str = Depends(get_admin_user),
):
    db = get_database()
    existing = await db.categories.find_one({"code": category.code})
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")

    category_dict = category.model_dump()
    result = await db.categories.insert_one(category_dict)
    created = await db.categories.find_one({"_id": result.inserted_id})

    return CategoryResponse(
        id=str(created["_id"]),
        name=created["name"],
        code=created["code"],
        icon=created.get("icon"),
        sort_order=created.get("sort_order", 0),
    )


router_admin = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router_admin.get("/sources", response_model=List[NewsSourceResponse])
async def get_sources(user_id: str = Depends(get_admin_user)):
    db = get_database()
    cursor = db.news_sources.find({})
    sources = await cursor.to_list(length=100)

    return [
        NewsSourceResponse(
            id=str(s["_id"]),
            name=s["name"],
            url=s["url"],
            type=s["type"],
            is_active=s.get("is_active", True),
            last_fetch_at=s.get("last_fetch_at"),
        )
        for s in sources
    ]


@router_admin.post("/sources", response_model=NewsSourceResponse)
async def create_source(
    source: NewsSourceCreate,
    user_id: str = Depends(get_admin_user),
):
    db = get_database()
    source_dict = source.model_dump()
    result = await db.news_sources.insert_one(source_dict)
    created = await db.news_sources.find_one({"_id": result.inserted_id})

    return NewsSourceResponse(
        id=str(created["_id"]),
        name=created["name"],
        url=created["url"],
        type=created["type"],
        is_active=created.get("is_active", True),
        last_fetch_at=created.get("last_fetch_at"),
    )


@router_admin.post("/refresh")
async def trigger_refresh(user_id: str = Depends(get_admin_user)):
    from app.agents.crawler_agent import run_crawler
    try:
        result = await run_crawler()
        return {"message": "Refresh completed", "status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
