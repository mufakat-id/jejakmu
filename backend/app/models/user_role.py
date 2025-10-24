import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.users.models import User


class UserRole(SQLModel, AuditMixin, table=True):
    """
    Junction table for many-to-many relationship between User and Role.
    Allows one user to have multiple roles.
    """

    __tablename__ = "user_role"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    role_id: uuid.UUID = Field(foreign_key="role.id", index=True)

    # Optional: Add extra fields for junction table
    is_active: bool = Field(
        default=True, description="Whether this role assignment is active"
    )

    # Relationships
    user: "User" = Relationship(back_populates="user_roles")
    role: "Role" = Relationship(back_populates="user_roles")
