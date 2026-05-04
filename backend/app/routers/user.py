from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from app.core.database import get_database
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.user import UserResponse, UserCreate, UserLogin, Token, HistoryItem, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id


async def get_admin_user(user_id: str = Depends(get_current_user)):
    from app.core.config import settings
    admin_ids = [aid.strip() for aid in settings.ADMIN_USER_IDS.split(",") if aid.strip()]
    if admin_ids and user_id not in admin_ids:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id


@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    db = get_database()
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user.email} if user.email else {},
            {"phone": user.phone} if user.phone else {},
        ]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.password)
    user_dict = {
        "email": user.email,
        "phone": user.phone,
        "nickname": user.nickname or f"User_{ObjectId()}",
        "avatar": None,
        "hashed_password": hashed_password,
        "favorites": [],
        "history": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)
    access_token = create_access_token(data={"sub": user_id})

    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = await db.users.find_one({"email": form_data.username})
    if not user:
        user = await db.users.find_one({"phone": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email/phone or password")

    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user.get("email"),
        phone=user.get("phone"),
        nickname=user.get("nickname"),
        avatar=user.get("avatar"),
        favorites=user.get("favorites", []),
        created_at=user["created_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user),
):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user.get("email"),
        phone=user.get("phone"),
        nickname=user.get("nickname"),
        avatar=user.get("avatar"),
        favorites=user.get("favorites", []),
        created_at=user["created_at"],
    )


@router.get("/favorites", response_model=List[dict])
async def get_favorites(user_id: str = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    favorite_ids = [ObjectId(fid) for fid in user.get("favorites", []) if ObjectId.is_valid(fid)]
    if not favorite_ids:
        return []

    favorites = await db.news.find({"_id": {"$in": favorite_ids}}).to_list(length=100)
    return [
        {
            "id": str(f["_id"]),
            "title": f["title"],
            "summary": f.get("summary"),
            "source_name": f["source_name"],
            "category": f["category"],
            "published_at": f["published_at"],
        }
        for f in favorites
    ]


@router.post("/favorites/{news_id}")
async def add_favorite(news_id: str, user_id: str = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    news = await db.news.find_one({"_id": ObjectId(news_id)})
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"favorites": news_id}}
    )

    return {"message": "Added to favorites"}


@router.delete("/favorites/{news_id}")
async def remove_favorite(news_id: str, user_id: str = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"favorites": news_id}}
    )

    return {"message": "Removed from favorites"}


@router.get("/history", response_model=List[dict])
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user),
):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = user.get("history", [])
    skip = (page - 1) * page_size
    paginated_history = history[skip:skip + page_size]

    if not paginated_history:
        return []

    history_ids = [ObjectId(h["news_id"]) for h in paginated_history if ObjectId.is_valid(h["news_id"])]
    news_map = {}
    if history_ids:
        news_list = await db.news.find({"_id": {"$in": history_ids}}).to_list(length=100)
        for n in news_list:
            news_map[str(n["_id"])] = n

    result = []
    for h in paginated_history:
        news_id = h["news_id"]
        if news_id in news_map:
            n = news_map[news_id]
            result.append({
                "id": str(n["_id"]),
                "title": n["title"],
                "summary": n.get("summary"),
                "source_name": n["source_name"],
                "viewed_at": h["viewed_at"],
            })

    return result


@router.post("/history/{news_id}")
async def add_history(news_id: str, user_id: str = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(news_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    news = await db.news.find_one({"_id": ObjectId(news_id)})
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    history_item = HistoryItem(news_id=news_id, viewed_at=datetime.now(timezone.utc))

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$pull": {"history": {"news_id": news_id}},
        }
    )
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$push": {"history": history_item.model_dump()},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        }
    )

    return {"message": "History added"}
