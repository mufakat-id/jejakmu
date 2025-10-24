import uuid

from sqlmodel import Session

from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.users.models import Role


class RoleService:
    """Service for role business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = RoleRepository(session)

    def create_role(self, role_in: RoleCreate) -> Role:
        """Create a new role"""
        # Business logic: Check if role already exists
        existing = self.repository.get_by_name(role_in.name)
        if existing:
            raise ValueError(f"Role with name '{role_in.name}' already exists")

        role_dict = role_in.model_dump()
        return self.repository.create(role_dict)

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        """Get role by ID"""
        return self.repository.get(role_id)

    def get_role_by_name(self, name: str) -> Role | None:
        """Get role by name"""
        return self.repository.get_by_name(name)

    def get_roles(self, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        """Get all roles with count"""
        roles = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return roles, count

    def get_active_roles(self) -> list[Role]:
        """Get all active roles"""
        return self.repository.get_active_roles()

    def update_role(self, db_role: Role, role_in: RoleUpdate) -> Role:
        """Update an existing role"""
        role_data = role_in.model_dump(exclude_unset=True)

        # Business logic: Check name uniqueness if being updated
        if "name" in role_data and role_data["name"] != db_role.name:
            existing = self.repository.get_by_name(role_data["name"])
            if existing:
                raise ValueError(f"Role with name '{role_data['name']}' already exists")

        return self.repository.update(db_role, role_data)

    def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete role by ID"""
        return self.repository.delete(role_id)
