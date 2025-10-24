import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.items.models import Item
    from app.models.user_cv import UserCV
    from app.models.user_profile import UserProfile
    from app.models.user_role import UserRole


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
