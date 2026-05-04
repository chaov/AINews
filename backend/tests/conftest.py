import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from datetime import datetime, timezone


@pytest.fixture
def sample_news_id():
    return str(ObjectId())


@pytest.fixture
def sample_user_id():
    return str(ObjectId())


@pytest.fixture
def sample_news_doc(sample_news_id):
    return {
        "_id": ObjectId(sample_news_id),
        "title": "Test News Title",
        "summary": "This is a test summary",
        "evaluation": "This is a test evaluation",
        "content": "Full content here",
        "source_name": "Test Source",
        "source_url": "https://example.com/news/1",
        "category": "tech",
        "tags": ["AI", "test"],
        "published_at": datetime.now(timezone.utc),
        "view_count": 10,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_user_doc(sample_user_id):
    return {
        "_id": ObjectId(sample_user_id),
        "email": "test@example.com",
        "phone": None,
        "nickname": "TestUser",
        "avatar": None,
        "hashed_password": "$2b$12$fakehashedpassword",
        "favorites": [],
        "history": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_category_doc():
    return {
        "_id": ObjectId(),
        "name": "科技",
        "code": "tech",
        "icon": "computer",
        "sort_order": 1,
        "is_active": True,
    }


@pytest.fixture
def sample_source_doc():
    return {
        "_id": ObjectId(),
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "type": "rss",
        "config": {},
        "is_active": True,
        "last_fetch_at": None,
    }
