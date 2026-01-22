"""Authentication routes."""

from fastapi import APIRouter, Depends

from backend.auth.dependencies import get_current_user
from backend.models.schemas import CurrentUser, SessionResponse

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.get("/session", response_model=SessionResponse)
async def get_session(
    current_user: CurrentUser = Depends(get_current_user)
) -> SessionResponse:
    """
    Get current user session information.

    Requires valid JWT token in Authorization header.
    Returns user information extracted from the token.
    """
    return SessionResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        authenticated=True,
    )
