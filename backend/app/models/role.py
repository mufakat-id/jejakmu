import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.models.user_role import UserRole


class Role(SQLModel, AuditMixin, table=True):
    """
    Role model for role-based access control (RBAC).

    Examples: 'admin', 'editor', 'viewer', 'manager', etc.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(
        unique=True,
        index=True,
        max_length=50,
        description="Role name (e.g., 'admin', 'editor')",
    )
    description: str | None = Field(
        default=None, max_length=255, description="Role description"
    )
    is_active: bool = Field(default=True, description="Whether this role is active")

    # Relationships
    user_roles: list["UserRole"] | None = Relationship(
        back_populates="role", cascade_delete=True
    )

    def __str__(self) -> str:
        return self.name
