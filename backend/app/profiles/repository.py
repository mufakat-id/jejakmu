import uuid

from sqlmodel import Session, select

from app.profiles.models import UserProfile
from app.repositories.base import BaseRepository


class UserProfileRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile-specific database operations"""

    def __init__(self, session: Session):
        super().__init__(UserProfile, session)

    def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        """Get profile by user ID"""
        statement = select(UserProfile).where(UserProfile.user_id == user_id)
        return self.session.exec(statement).first()

    def create_profile(self, user_id: uuid.UUID, profile_data: dict) -> UserProfile:
        """Create a new profile for a user"""
        profile = UserProfile(user_id=user_id, **profile_data)
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile
