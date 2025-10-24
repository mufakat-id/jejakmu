import uuid
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from app.models import User
from app.repositories.base import BaseRepository
from app.users.models import Role, UserRole

if TYPE_CHECKING:
    pass


class RoleRepository(BaseRepository[Role]):
    """Repository for Role-specific database operations"""

    def __init__(self, session: Session):
        super().__init__(Role, session)

    def get_by_name(self, name: str) -> Role | None:
        """Get role by name"""
        statement = select(Role).where(Role.name == name)
        return self.session.exec(statement).first()

    def get_active_roles(self) -> list[Role]:
        """Get all active roles"""
        statement = select(Role).where(Role.is_active == True)  # noqa: E712
        return list(self.session.exec(statement).all())


class UserRoleRepository(BaseRepository[UserRole]):
    """Repository for UserRole-specific database operations"""

    def __init__(self, session: Session):
        super().__init__(UserRole, session)

    def get_by_user_id(self, user_id: uuid.UUID) -> list[UserRole]:
        """Get all roles for a specific user"""
        statement = select(UserRole).where(UserRole.user_id == user_id)
        return list(self.session.exec(statement).all())

    def get_user_roles_with_details(self, user_id: uuid.UUID) -> list[Role]:
        """Get all role objects for a specific user"""
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(UserRole.is_active == True)  # noqa: E712
        )
        return list(self.session.exec(statement).all())

    def has_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        """Check if user has a specific role"""
        statement = (
            select(UserRole)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
            .where(Role.name == role_name)
            .where(UserRole.is_active == True)  # noqa: E712
        )
        return self.session.exec(statement).first() is not None

    def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        """Assign a role to a user"""
        # Check if already exists
        statement = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        existing = self.session.exec(statement).first()

        if existing:
            # Reactivate if inactive
            if not existing.is_active:
                existing.is_active = True
                self.session.add(existing)
                self.session.commit()
                self.session.refresh(existing)
            return existing

        # Create new
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        self.session.commit()
        self.session.refresh(user_role)
        return user_role

    def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove a role from a user"""
        statement = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        user_role = self.session.exec(statement).first()

        if user_role:
            self.session.delete(user_role)
            self.session.commit()
            return True
        return False


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
