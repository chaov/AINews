import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_wrong_password():
    hashed = get_password_hash("correctpassword")
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token():
    data = {"sub": "test_user_id"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user_id"


def test_decode_invalid_token():
    payload = decode_access_token("invalid.token.here")
    assert payload is None


def test_token_contains_expiration():
    data = {"sub": "test_user_id"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload is not None
    assert "exp" in payload


def test_create_token_with_custom_expiry():
    from datetime import timedelta
    data = {"sub": "test_user_id"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user_id"
