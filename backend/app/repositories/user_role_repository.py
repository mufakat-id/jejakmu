import uuid
from sqlmodel import Session, select

from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.base import BaseRepository


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
            .where(UserRole.is_active == True)
        )
        return list(self.session.exec(statement).all())

    def has_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        """Check if user has a specific role"""
        statement = (
            select(UserRole)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
            .where(Role.name == role_name)
            .where(UserRole.is_active == True)
        )
        return self.session.exec(statement).first() is not None

    def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        """Assign a role to a user"""
        # Check if already exists
        statement = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
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
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        user_role = self.session.exec(statement).first()

        if user_role:
            self.session.delete(user_role)
            self.session.commit()
            return True
        return False

