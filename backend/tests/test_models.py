import pytest
from app.models.news import NewsCreate, NewsUpdate, NewsResponse
from app.models.user import UserCreate, UserUpdate, UserResponse, Token, HistoryItem
from app.models.source import CategoryCreate, CategoryResponse, NewsSourceCreate, NewsSourceResponse
from datetime import datetime, timezone


class TestNewsModels:
    def test_news_create(self):
        news = NewsCreate(
            title="Test Title",
            summary="Test Summary",
            source_name="Test Source",
            source_url="https://example.com",
            category="tech",
            tags=["AI"],
            published_at=datetime.now(timezone.utc),
        )
        assert news.title == "Test Title"
        assert news.category == "tech"
        assert news.is_active is True
        assert news.tags == ["AI"]

    def test_news_create_defaults(self):
        news = NewsCreate(
            title="Test",
            source_name="Source",
            source_url="https://example.com",
            category="tech",
            published_at=datetime.now(timezone.utc),
        )
        assert news.summary is None
        assert news.evaluation is None
        assert news.content is None
        assert news.tags == []
        assert news.is_active is True

    def test_news_update_partial(self):
        update = NewsUpdate(title="New Title")
        data = update.model_dump()
        assert data["title"] == "New Title"
        assert data["summary"] is None
        assert data["category"] is None

    def test_news_response(self):
        now = datetime.now(timezone.utc)
        response = NewsResponse(
            id="507f1f77bcf86cd799439011",
            title="Test",
            summary="Summary",
            evaluation="Eval",
            source_name="Source",
            source_url="https://example.com",
            category="tech",
            tags=["AI"],
            published_at=now,
            view_count=5,
            is_active=True,
        )
        assert response.id == "507f1f77bcf86cd799439011"
        assert response.view_count == 5


class TestUserModels:
    def test_user_create_with_email(self):
        user = UserCreate(
            email="test@example.com",
            password="password123",
            nickname="TestUser",
        )
        assert user.email == "test@example.com"
        assert user.phone is None
        assert user.password == "password123"

    def test_user_create_with_phone(self):
        user = UserCreate(
            phone="13800138000",
            password="password123",
        )
        assert user.phone == "13800138000"
        assert user.email is None

    def test_user_update(self):
        update = UserUpdate(nickname="NewNick")
        data = update.model_dump()
        assert data["nickname"] == "NewNick"
        assert data["avatar"] is None

    def test_token_model(self):
        token = Token(access_token="abc123")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_history_item(self):
        now = datetime.now(timezone.utc)
        item = HistoryItem(news_id="507f1f77bcf86cd799439011", viewed_at=now)
        assert item.news_id == "507f1f77bcf86cd799439011"
        assert item.viewed_at == now


class TestCategoryModels:
    def test_category_create(self):
        cat = CategoryCreate(
            name="科技",
            code="tech",
            icon="computer",
            sort_order=1,
        )
        assert cat.name == "科技"
        assert cat.code == "tech"
        assert cat.is_active is True

    def test_category_response(self):
        cat = CategoryResponse(
            id="507f1f77bcf86cd799439011",
            name="科技",
            code="tech",
            icon="computer",
            sort_order=1,
        )
        assert cat.id == "507f1f77bcf86cd799439011"


class TestSourceModels:
    def test_source_create(self):
        source = NewsSourceCreate(
            name="BBC",
            url="http://feeds.bbci.co.uk/news/rss.xml",
            type="rss",
        )
        assert source.name == "BBC"
        assert source.type == "rss"
        assert source.is_active is True
        assert source.config == {}

    def test_source_response(self):
        source = NewsSourceResponse(
            id="507f1f77bcf86cd799439011",
            name="BBC",
            url="http://feeds.bbci.co.uk/news/rss.xml",
            type="rss",
            is_active=True,
            last_fetch_at=None,
        )
        assert source.id == "507f1f77bcf86cd799439011"
        assert source.last_fetch_at is None
