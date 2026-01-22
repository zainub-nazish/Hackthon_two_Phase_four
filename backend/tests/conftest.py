"""Test configuration and fixtures for JWT authentication and database tests."""

import asyncio
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Test secret - only for testing, never use in production
TEST_SECRET = "test-secret-key-for-jwt-testing-must-be-32-chars-or-more"
TEST_ALGORITHM = "HS256"

# Test database URL - use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_id() -> str:
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def another_user_id() -> str:
    """Generate another test user ID for cross-user testing."""
    return str(uuid4())


@pytest.fixture
def valid_token(test_user_id: str) -> str:
    """
    Create a valid JWT token for testing.

    Token contains:
    - sub: user ID
    - exp: 1 hour from now
    - iat: current time
    - email: test email
    """
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now + 3600,  # 1 hour from now
        "iat": now,
        "email": "test@example.com",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def another_user_token(another_user_id: str) -> str:
    """Create a valid JWT token for another user (cross-user testing)."""
    now = int(time.time())
    payload = {
        "sub": another_user_id,
        "exp": now + 3600,
        "iat": now,
        "email": "another@example.com",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def expired_token(test_user_id: str) -> str:
    """
    Create an expired JWT token for testing expiration handling.

    Token expired 1 hour ago.
    """
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now - 3600,  # Expired 1 hour ago
        "iat": now - 7200,  # Issued 2 hours ago
        "email": "test@example.com",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def token_near_expiry(test_user_id: str) -> str:
    """
    Create a token that is about to expire (within clock skew tolerance).

    Token expires in 5 seconds (within 10s leeway).
    """
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now + 5,  # Expires in 5 seconds
        "iat": now - 3595,  # Issued almost 1 hour ago
        "email": "test@example.com",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def token_within_clock_skew(test_user_id: str) -> str:
    """
    Create a token that appears expired but is within clock skew tolerance.

    Token "expired" 5 seconds ago, but should still be valid with 10s leeway.
    """
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now - 5,  # "Expired" 5 seconds ago
        "iat": now - 3605,
        "email": "test@example.com",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def malformed_token() -> str:
    """Create a malformed token (invalid JWT structure)."""
    return "not.a.valid.jwt.token"


@pytest.fixture
def wrong_signature_token(test_user_id: str) -> str:
    """Create a token signed with wrong secret."""
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now + 3600,
        "iat": now,
        "email": "test@example.com",
    }
    return jwt.encode(payload, "wrong-secret-key-that-is-definitely-different", algorithm=TEST_ALGORITHM)


@pytest.fixture
def tampered_token(valid_token: str) -> str:
    """
    Create a tampered token by modifying the payload after signing.

    Changes the payload portion of the JWT without re-signing.
    """
    parts = valid_token.split(".")
    # Modify the payload (middle part) - this breaks the signature
    import base64
    payload_b64 = parts[1]
    # Add padding if needed
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding
    # Decode, modify, re-encode
    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    # Just modify a byte to tamper
    tampered_bytes = payload_bytes[:-1] + bytes([payload_bytes[-1] ^ 0xFF])
    tampered_b64 = base64.urlsafe_b64encode(tampered_bytes).decode().rstrip("=")
    return f"{parts[0]}.{tampered_b64}.{parts[2]}"


@pytest.fixture
def token_missing_sub() -> str:
    """Create a token without the required 'sub' claim."""
    now = int(time.time())
    payload = {
        "exp": now + 3600,
        "iat": now,
        "email": "test@example.com",
        # Note: 'sub' is intentionally missing
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def token_missing_exp(test_user_id: str) -> str:
    """Create a token without the required 'exp' claim."""
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "iat": now,
        "email": "test@example.com",
        # Note: 'exp' is intentionally missing
    }
    # jwt.encode doesn't take options, it just encodes what we give it
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def token_missing_iat(test_user_id: str) -> str:
    """Create a token without the required 'iat' claim."""
    now = int(time.time())
    payload = {
        "sub": test_user_id,
        "exp": now + 3600,
        "email": "test@example.com",
        # Note: 'iat' is intentionally missing
    }
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client with mocked settings and test database.

    Patches BETTER_AUTH_SECRET and DATABASE_URL for testing.
    Uses SQLite in-memory database for fast, isolated tests.
    """
    import os

    # Set test environment variables before importing the app
    os.environ["BETTER_AUTH_SECRET"] = TEST_SECRET
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

    # Need to reload modules to pick up new environment variables
    # Force reimport to get fresh settings
    import importlib
    import backend.config
    import backend.database
    import backend.main
    import backend.routes.tasks

    importlib.reload(backend.config)
    importlib.reload(backend.database)
    importlib.reload(backend.routes.tasks)
    importlib.reload(backend.main)

    from backend.main import app

    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for async tests.

    Uses SQLite in-memory database for fast, isolated tests.
    """
    import os

    # Set test environment variables
    os.environ["BETTER_AUTH_SECRET"] = TEST_SECRET
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

    # Force reimport to get fresh settings
    import importlib
    import backend.config
    import backend.database
    import backend.main
    import backend.routes.tasks

    importlib.reload(backend.config)
    importlib.reload(backend.database)
    importlib.reload(backend.routes.tasks)
    importlib.reload(backend.main)

    from backend.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def auth_header(valid_token: str) -> dict[str, str]:
    """Create Authorization header with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def another_user_auth_header(another_user_token: str) -> dict[str, str]:
    """Create Authorization header for another user."""
    return {"Authorization": f"Bearer {another_user_token}"}
