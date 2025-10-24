from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.users.models import Role


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
