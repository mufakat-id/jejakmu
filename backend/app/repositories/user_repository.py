from typing import TYPE_CHECKING

from sqlmodel import Session, select

from app.models import User
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from app.models.user import UserRole


class UserRepository(BaseRepository[User]):
    """Repository for User model with custom queries"""

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True).offset(skip).limit(limit)  # noqa: E712
        return list(self.session.exec(statement).all())

    def get_superusers(self) -> list[User]:
        """Get all superusers"""
        statement = select(User).where(User.is_superuser == True)  # noqa: E712
        return list(self.session.exec(statement).all())
