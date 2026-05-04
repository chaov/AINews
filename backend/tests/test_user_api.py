import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token, get_password_hash


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
def test_user_id():
    return str(ObjectId())


@pytest.fixture
def auth_token(test_user_id):
    return create_access_token(data={"sub": test_user_id})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.mark.asyncio
async def test_register_new_user(mock_db, test_user_id):
    mock_db.users.find_one = AsyncMock(return_value=None)
    mock_db.users.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId(test_user_id)))

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/users/register", json={
                    "email": "newuser@example.com",
                    "password": "password123",
                    "nickname": "NewUser",
                })
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_user(mock_db):
    mock_db.users.find_one = AsyncMock(return_value={"_id": ObjectId(), "email": "existing@example.com"})

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/users/register", json={
                    "email": "existing@example.com",
                    "password": "password123",
                })
                assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(mock_db, test_user_id):
    hashed = get_password_hash("password123")
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "email": "test@example.com",
        "hashed_password": hashed,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/users/login", data={
                    "username": "test@example.com",
                    "password": "password123",
                })
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(mock_db):
    hashed = get_password_hash("correctpassword")
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(),
        "email": "test@example.com",
        "hashed_password": hashed,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/users/login", data={
                    "username": "test@example.com",
                    "password": "wrongpassword",
                })
                assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(mock_db):
    mock_db.users.find_one = AsyncMock(return_value=None)

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post("/api/v1/users/login", data={
                    "username": "nonexistent@example.com",
                    "password": "password123",
                })
                assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(mock_db, test_user_id, auth_headers):
    now = datetime.now(timezone.utc)
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "email": "test@example.com",
        "phone": None,
        "nickname": "TestUser",
        "avatar": None,
        "favorites": [],
        "created_at": now,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/users/me", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["nickname"] == "TestUser"


@pytest.mark.asyncio
async def test_get_current_user_no_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.main.start_scheduler"), \
             patch("app.main.initialize_default_data", new_callable=AsyncMock), \
             patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
             patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
            response = await client.get("/api/v1/users/me")
            assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_profile(mock_db, test_user_id, auth_headers):
    now = datetime.now(timezone.utc)
    mock_db.users.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "email": "test@example.com",
        "phone": None,
        "nickname": "UpdatedNick",
        "avatar": None,
        "favorites": [],
        "created_at": now,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.put(
                    "/api/v1/users/me",
                    json={"nickname": "UpdatedNick"},
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert data["nickname"] == "UpdatedNick"


@pytest.mark.asyncio
async def test_get_favorites_empty(mock_db, test_user_id, auth_headers):
    now = datetime.now(timezone.utc)
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "favorites": [],
        "created_at": now,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/users/favorites", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert data == []


@pytest.mark.asyncio
async def test_add_favorite(mock_db, test_user_id, auth_headers):
    news_id = str(ObjectId())
    now = datetime.now(timezone.utc)
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "favorites": [],
        "created_at": now,
    })
    mock_db.news.find_one = AsyncMock(return_value={
        "_id": ObjectId(news_id),
        "title": "Test News",
    })
    mock_db.users.update_one = AsyncMock(return_value=MagicMock(modified_count=1))

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post(
                    f"/api/v1/users/favorites/{news_id}",
                    headers=auth_headers,
                )
                assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_favorite_invalid_news_id(mock_db, test_user_id, auth_headers):
    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post(
                    "/api/v1/users/favorites/invalid-id",
                    headers=auth_headers,
                )
                assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_history_empty(mock_db, test_user_id, auth_headers):
    now = datetime.now(timezone.utc)
    mock_db.users.find_one = AsyncMock(return_value={
        "_id": ObjectId(test_user_id),
        "history": [],
        "created_at": now,
    })

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.get("/api/v1/users/history", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert data == []


@pytest.mark.asyncio
async def test_add_history(mock_db, test_user_id, auth_headers):
    news_id = str(ObjectId())
    now = datetime.now(timezone.utc)
    mock_db.news.find_one = AsyncMock(return_value={
        "_id": ObjectId(news_id),
        "title": "Test News",
    })
    mock_db.users.update_one = AsyncMock(return_value=MagicMock(modified_count=1))

    with patch("app.routers.user.get_database", return_value=mock_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.main.start_scheduler"), \
                 patch("app.main.initialize_default_data", new_callable=AsyncMock), \
                 patch("app.core.database.connect_to_mongodb", new_callable=AsyncMock), \
                 patch("app.core.database.close_mongodb_connection", new_callable=AsyncMock):
                response = await client.post(
                    f"/api/v1/users/history/{news_id}",
                    headers=auth_headers,
                )
                assert response.status_code == 200
