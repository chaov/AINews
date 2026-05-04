import pytest
import os
from app.core.config import Settings


class TestSettings:
    def test_default_settings_values(self):
        settings = Settings(
            MONGODB_URL="mongodb://localhost:27017",
            MONGODB_DB_NAME="ai_news",
            SECRET_KEY="test-secret",
        )
        assert settings.APP_NAME == "AI News API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is True
        assert settings.MONGODB_URL == "mongodb://localhost:27017"
        assert settings.MONGODB_DB_NAME == "ai_news"
        assert settings.CRAWLER_INTERVAL_MINUTES == 60

    def test_custom_settings(self):
        settings = Settings(
            MONGODB_URL="mongodb://custom:27017",
            MONGODB_DB_NAME="test_db",
            SECRET_KEY="test-secret",
            DEBUG=False,
        )
        assert settings.MONGODB_URL == "mongodb://custom:27017"
        assert settings.MONGODB_DB_NAME == "test_db"
        assert settings.DEBUG is False

    def test_secret_key_configurable(self):
        settings = Settings(SECRET_KEY="my-custom-secret")
        assert settings.SECRET_KEY == "my-custom-secret"

    def test_algorithm_default(self):
        settings = Settings(SECRET_KEY="test")
        assert settings.ALGORITHM == "HS256"

    def test_token_expire_default(self):
        settings = Settings(SECRET_KEY="test")
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 7

    def test_llm_settings_default(self):
        settings = Settings(SECRET_KEY="test")
        assert not settings.LLM_PROVIDER
        assert not settings.LLM_API_KEY
        assert not settings.LLM_MODEL

    def test_admin_user_ids_default(self):
        settings = Settings(SECRET_KEY="test")
        assert settings.ADMIN_USER_IDS == ""
