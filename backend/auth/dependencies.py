"""Authentication dependencies for FastAPI routes."""

import httpx
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import settings
from backend.models.schemas import CurrentUser

# HTTPBearer security scheme - extracts Bearer token from Authorization header
security = HTTPBearer(
    description="Better Auth session token",
    auto_error=True
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Verify session token via Better Auth's /api/auth/get-session endpoint.

    Better Auth bearer plugin converts Authorization: Bearer <token>
    to a session lookup and returns user data.

    Raises:
        HTTPException: 401 Unauthorized for any verification failure
    """
    token = credentials.credentials
    import logging
    log = logging.getLogger("auth")
    log.warning(f"[AUTH] token received: {token[:10]}... len={len(token)}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.better_auth_url}/api/auth/get-session",
                headers={"Authorization": f"Bearer {token}"},
            )
        log.warning(f"[AUTH] get-session status={response.status_code} body={response.text[:200]}")
    except httpx.RequestError as e:
        log.warning(f"[AUTH] get-session request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth service unreachable",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = response.json()
    user = data.get("user") if data else None

    if not user or not user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        user_id=user["id"],
        email=user.get("email", ""),
    )


async def verify_user_owns_resource(
    user_id: str = Path(..., description="User ID from URL path"),
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Verify that the authenticated user matches the user_id in the URL path.

    Returns 404 (not 403) to prevent information leakage about resource existence.
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    return current_user
