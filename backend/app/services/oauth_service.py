import logging

import httpx
from authlib.integrations.starlette_client import OAuth
from sqlmodel import Session
from starlette.config import Config

from app.core.config import settings
from app.models import User
from app.repositories import UserRepository

logger = logging.getLogger(__name__)

# Initialize OAuth with Starlette Config
# This is required for Authlib to work properly
starlette_config = Config(
    environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID or "",
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET or "",
    }
)

oauth = OAuth(starlette_config)

# Register Google OAuth2
if settings.google_oauth_enabled:
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
        },
    )


class OAuthService:
    """Service for OAuth authentication"""

    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)

    def link_google_account(
        self, google_id: str, email: str, full_name: str | None = None
    ) -> User | None:
        """Link Google account to existing user, return None if user doesn't exist"""
        # Try to find user by google_id first (already linked)
        from sqlmodel import select

        statement = select(User).where(User.google_id == google_id)
        user = self.session.exec(statement).first()

        if user:
            return user

        # Try to find by email (must exist in database)
        user = self.user_repository.get_by_email(email)
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            if not user.full_name and full_name:
                user.full_name = full_name
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user

        # User doesn't exist - return None
        return None

    def create_or_link_google_account(
        self, google_id: str, email: str, full_name: str | None = None
    ) -> User:
        """Create new user or link Google account to existing user"""
        # Try to find user by google_id first (already linked)
        from sqlmodel import select
        import secrets
        from app.models import Role, UserRole

        statement = select(User).where(User.google_id == google_id)
        user = self.session.exec(statement).first()

        if user:
            return user

        # Try to find by email
        user = self.user_repository.get_by_email(email)
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            if not user.full_name and full_name:
                user.full_name = full_name
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user

        # User doesn't exist - create new user
        new_user = User(
            email=email,
            full_name=full_name or email.split("@")[0],
            google_id=google_id,
            is_active=True,
            is_superuser=False,
            # Generate random password since user will login via Google
            hashed_password=secrets.token_urlsafe(32),
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        # Automatically assign 'talent' role to new user
        talent_role = self.session.exec(
            select(Role).where(Role.name == "talent")
        ).first()

        if talent_role:
            user_role = UserRole(
                user_id=new_user.id,
                role_id=talent_role.id,
                is_active=True,
            )
            self.session.add(user_role)
            self.session.commit()

        return new_user

    async def exchange_google_code_for_user_info(self, code: str) -> dict | None:
        """Exchange Google authorization code for user information"""
        if not settings.google_oauth_enabled:
            return None

        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "postmessage",  # Standard for @react-oauth/google
        }

        async with httpx.AsyncClient() as client:
            try:
                # Get access token
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()

                access_token = token_info.get("access_token")
                if not access_token:
                    return None

                # Get user info using access token
                userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}

                userinfo_response = await client.get(userinfo_url, headers=headers)
                userinfo_response.raise_for_status()
                user_info = userinfo_response.json()

                return {
                    "google_id": user_info.get("id"),
                    "email": user_info.get("email"),
                    "full_name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "verified_email": user_info.get("verified_email", False),
                }

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                # Log error details for debugging
                logger.error(
                    "Google OAuth token exchange failed: %s",
                    {
                        "error": str(e),
                        "response_status": getattr(e, "response", None)
                        and e.response.status_code,
                        "response_body": getattr(e, "response", None)
                        and e.response.text,
                        "request_url": str(e.request.url)
                        if hasattr(e, "request")
                        else None,
                    },
                )
                return None
