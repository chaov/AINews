from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.routers import news, user, admin
from app.services.scheduler_service import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    await initialize_default_data()
    start_scheduler()
    yield
    from app.services.scheduler_service import scheduler
    scheduler.shutdown()
    await close_mongodb_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(admin.router_admin)


@app.get("/")
async def root():
    return {"message": "AI News API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def initialize_default_data():
    from app.core.database import get_database

    db = get_database()

    await db.news.create_index("category")
    await db.news.create_index("is_active")
    await db.news.create_index([("published_at", -1)])
    await db.news.create_index([("title", "text"), ("summary", "text")])
    await db.news.create_index("source_url")
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("phone", unique=True, sparse=True)
    await db.categories.create_index("code", unique=True)
    await db.news_sources.create_index("url", unique=True)

    default_categories = [
        {"name": "科技", "code": "tech", "icon": "computer", "sort_order": 1},
        {"name": "财经", "code": "finance", "icon": "trending_up", "sort_order": 2},
        {"name": "教育", "code": "education", "icon": "school", "sort_order": 3},
        {"name": "健康", "code": "health", "icon": "favorite", "sort_order": 4},
        {"name": "娱乐", "code": "entertainment", "icon": "movie", "sort_order": 5},
        {"name": "体育", "code": "sports", "icon": "sports", "sort_order": 6},
        {"name": "国际", "code": "world", "icon": "public", "sort_order": 7},
    ]

    for cat in default_categories:
        existing = await db.categories.find_one({"code": cat["code"]})
        if not existing:
            await db.categories.insert_one({**cat, "is_active": True})

    default_sources = [
        {
            "name": "BBC News",
            "url": "http://feeds.bbci.co.uk/news/rss.xml",
            "type": "rss",
            "config": {},
            "is_active": True,
        },
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "type": "rss",
            "config": {},
            "is_active": True,
        },
    ]

    for source in default_sources:
        existing = await db.news_sources.find_one({"url": source["url"]})
        if not existing:
            await db.news_sources.insert_one(source)

    print("Default data initialized")
