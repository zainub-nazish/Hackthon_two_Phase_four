"""Authentication dependencies for FastAPI routes."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.schemas import CurrentUser

# HTTPBearer security scheme - extracts Bearer token from Authorization header
security = HTTPBearer(
    description="Session token from Better Auth",
    auto_error=True  # Automatically return 401 if no token
)


async def get_auth_db_session():
    """Get database session for auth verification."""
    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    from backend.database import get_session
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_auth_db_session)
) -> CurrentUser:
    """
    Verify session token directly against the database.

    This dependency:
    1. Extracts token from Authorization: Bearer <token> header
    2. Looks up session in database (shared with Better Auth)
    3. Verifies session is not expired
    4. Returns user info

    Raises:
        HTTPException: 401 Unauthorized for any verification failure
    """
    token = credentials.credentials

    try:
        # Query session and user from database
        # Better Auth stores sessions in "session" table with "token" column
        result = await db.execute(
            text("""
                SELECT s.user_id, s.expires_at, u.email
                FROM "session" s
                JOIN "user" u ON s.user_id = u.id
                WHERE s.token = :token
            """),
            {"token": token}
        )
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_id, expires_at, email = row

        # Check if session is expired (compare naive datetimes)
        now = datetime.utcnow()
        if expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return CurrentUser(
            user_id=user_id,
            email=email
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Auth error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def verify_user_owns_resource(
    user_id: str = Path(..., description="User ID from URL path"),
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Verify that the authenticated user matches the user_id in the URL path.

    This prevents users from accessing other users' resources (IDOR prevention).
    Returns 404 (not 403) to prevent information leakage about resource existence.
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    return current_user
