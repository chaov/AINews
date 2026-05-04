import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.news = MagicMock()
    db.users = MagicMock()
    db.categories = MagicMock()
    db.news_sources = MagicMock()
    return db


@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": str(ObjectId())})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def make_async_cursor(results):
    cursor = MagicMock()
    cursor.sort = MagicMock(return_value=cursor)
    cursor.skip = MagicMock(return_value=cursor)
    cursor.limit = MagicMock(return_value=cursor)
    cursor.to_list = AsyncMock(return_value=results)
    return cursor


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "AI News API"
            assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_news_list(mock_db):
    news_id = str(ObjectId())
    now = datetime.now(timezone.utc)
    mock_db.news.find.return_value = make_async_cursor([{
        "_id": ObjectId(news_id),
        "title": "Test News",
        "summary": "Summary",
        "evaluation": "Evaluation",
        "source_name": "Source",
        "source_url": "https://example.com",
        "category": "tech",
        "tags": ["AI"],
        "published_at": now,
        "view_count": 5,
        "is_active": True,
    }])

    with patch("app.routers.news.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/news")
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0]["title"] == "Test News"
                assert data[0]["category"] == "tech"


@pytest.mark.asyncio
async def test_get_news_list_with_category(mock_db):
    mock_db.news.find.return_value = make_async_cursor([])

    with patch("app.routers.news.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/news?category=tech")
                assert response.status_code == 200

    call_args = mock_db.news.find.call_args
    assert call_args[0][0]["category"] == "tech"


@pytest.mark.asyncio
async def test_get_news_detail_invalid_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.get("/api/v1/news/invalid-id")
            assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_news_detail_not_found(mock_db):
    mock_db.news.find_one = AsyncMock(return_value=None)

    with patch("app.routers.news.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                valid_id = str(ObjectId())
                response = await client.get(f"/api/v1/news/{valid_id}")
                assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_news(mock_db):
    now = datetime.now(timezone.utc)
    mock_db.news.find.return_value = make_async_cursor([{
        "_id": ObjectId(),
        "title": "AI Breakthrough",
        "summary": "New AI model released",
        "evaluation": "Impressive",
        "source_name": "TechNews",
        "source_url": "https://example.com/2",
        "category": "tech",
        "tags": ["AI"],
        "published_at": now,
        "view_count": 0,
        "is_active": True,
    }])

    with patch("app.routers.news.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/news/search?q=AI")
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert "AI" in data[0]["title"]


@pytest.mark.asyncio
async def test_search_news_missing_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.get("/api/v1/news/search")
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_news(mock_db):
    news_id = str(ObjectId())
    now = datetime.now(timezone.utc)
    mock_db.news.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId(news_id)))
    mock_db.news.find_one = AsyncMock(return_value={
        "_id": ObjectId(news_id),
        "title": "New News",
        "summary": "New Summary",
        "evaluation": None,
        "content": None,
        "source_name": "Source",
        "source_url": "https://example.com/new",
        "category": "tech",
        "tags": [],
        "published_at": now,
        "view_count": 0,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })

    with patch("app.routers.news.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/news", json={
                    "title": "New News",
                    "summary": "New Summary",
                    "source_name": "Source",
                    "source_url": "https://example.com/new",
                    "category": "tech",
                    "published_at": now.isoformat(),
                })
                assert response.status_code == 200
                data = response.json()
                assert data["title"] == "New News"


@pytest.mark.asyncio
async def test_delete_news_invalid_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.delete("/api/v1/news/invalid-id")
            assert response.status_code == 400
