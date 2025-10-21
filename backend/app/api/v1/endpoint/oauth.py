from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.api.v1.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.schemas import GoogleAuthRequest, GoogleAuthResponse, UserPublic
from app.services import OAuthService

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/google", response_model=GoogleAuthResponse)
async def google_login(
    session: SessionDep, auth_request: GoogleAuthRequest
) -> GoogleAuthResponse:
    """
    Google OAuth Login

    Exchange Google authorization code for access token.
    This endpoint will:
    1. Validate the Google authorization code
    2. Get user info from Google
    3. Create new user or link Google account to existing user
    4. Return access token for the user

    Note: If user doesn't exist, a new account will be created automatically.
    """
    if not settings.google_oauth_enabled:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
        )

    oauth_service = OAuthService(session)

    # Exchange code for user info
    user_info = await oauth_service.exchange_google_code_for_user_info(
        auth_request.code
    )

    if not user_info:
        raise HTTPException(
            status_code=400,
            detail="Failed to authenticate with Google. Invalid authorization code.",
        )

    # Create new user or link Google account to existing user
    user = oauth_service.create_or_link_google_account(
        google_id=user_info["google_id"],
        email=user_info["email"],
        full_name=user_info.get("full_name"),
    )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    return GoogleAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic.model_validate(user),
    )
