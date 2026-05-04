import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token


def make_async_cursor(results):
    cursor = MagicMock()
    cursor.sort = MagicMock(return_value=cursor)
    cursor.skip = MagicMock(return_value=cursor)
    cursor.limit = MagicMock(return_value=cursor)
    cursor.to_list = AsyncMock(return_value=results)
    return cursor


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.news = MagicMock()
    db.users = MagicMock()
    db.categories = MagicMock()
    db.news_sources = MagicMock()
    return db


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": str(ObjectId())})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_categories(mock_db):
    mock_db.categories.find.return_value = make_async_cursor([{
        "_id": ObjectId(),
        "name": "科技",
        "code": "tech",
        "icon": "computer",
        "sort_order": 1,
        "is_active": True,
    }])

    with patch("app.routers.admin.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/categories")
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0]["name"] == "科技"
                assert data[0]["code"] == "tech"


@pytest.mark.asyncio
async def test_create_category(mock_db, auth_headers):
    cat_id = str(ObjectId())
    mock_db.categories.find_one = AsyncMock(return_value=None)
    mock_db.categories.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId(cat_id)))

    def find_one_side_effect(query):
        if "_id" in query:
            return AsyncMock(return_value={
                "_id": ObjectId(cat_id),
                "name": "新分类",
                "code": "new_cat",
                "icon": "star",
                "sort_order": 10,
                "is_active": True,
            })()
        return AsyncMock(return_value=None)()

    mock_db.categories.find_one = AsyncMock(side_effect=[
        None,
        {
            "_id": ObjectId(cat_id),
            "name": "新分类",
            "code": "new_cat",
            "icon": "star",
            "sort_order": 10,
            "is_active": True,
        },
    ])

    with patch("app.routers.admin.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post(
                    "/api/v1/categories",
                    json={"name": "新分类", "code": "new_cat", "icon": "star", "sort_order": 10},
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "新分类"


@pytest.mark.asyncio
async def test_create_duplicate_category(mock_db, auth_headers):
    mock_db.categories.find_one = AsyncMock(return_value={
        "_id": ObjectId(),
        "code": "tech",
    })

    with patch("app.routers.admin.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post(
                    "/api/v1/categories",
                    json={"name": "科技", "code": "tech"},
                    headers=auth_headers,
                )
                assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_sources(mock_db, auth_headers):
    mock_db.news_sources.find.return_value = make_async_cursor([{
        "_id": ObjectId(),
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "type": "rss",
        "is_active": True,
        "last_fetch_at": None,
    }])

    with patch("app.routers.admin.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/admin/sources", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert data[0]["name"] == "BBC News"


@pytest.mark.asyncio
async def test_admin_refresh(mock_db, auth_headers):
    with patch("app.agents.crawler_agent.run_crawler", new_callable=AsyncMock) as mock_crawler:
        mock_crawler.return_value = {"crawled": 5, "sources": 2}

        with patch("app.routers.admin.get_database", return_value=mock_db):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                with patch("app.main.start_scheduler"), \
                     patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                     patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                     patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                    response = await client.post("/api/v1/admin/refresh", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "success"
                    assert data["result"]["crawled"] == 5


@pytest.mark.asyncio
async def test_admin_refresh_no_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.post("/api/v1/admin/refresh")
            assert response.status_code == 401
