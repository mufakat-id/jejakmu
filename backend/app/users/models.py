import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.items.models import Item
    from app.models.user_cv import UserCV
    from app.profiles.models import UserProfile


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


class User(SQLModel, AuditMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    hashed_password: str | None = Field(default=None)  # Optional for OAuth users
    google_id: str | None = Field(
        default=None, unique=True, index=True
    )  # Google OAuth ID

    # Relationships
    items: list["Item"] | None = Relationship(
        back_populates="owner", cascade_delete=True
    )
    user_roles: list["UserRole"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    profile: "UserProfile" = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False},
    )
    cv: "UserCV" = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False},
    )
