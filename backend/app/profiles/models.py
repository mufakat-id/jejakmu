import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.sites.models import Site
    from app.users.models import User


class UserProfile(SQLModel, AuditMixin, table=True):
    """
    User profile model with extended information and site associations.
    Each user has one profile, and each profile can be associated with multiple sites.
    """

    __tablename__ = "user_profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
    site_id: uuid.UUID = Field(foreign_key="site.id", index=True)

    # Profile information
    phone: str | None = Field(default=None, max_length=20, description="Phone number")
    address: str | None = Field(default=None, max_length=500, description="Address")
    bio: str | None = Field(
        default=None, max_length=1000, description="Bio/description"
    )
    avatar_url: str | None = Field(
        default=None, max_length=500, description="Avatar image URL"
    )
    date_of_birth: str | None = Field(
        default=None, description="Date of birth (YYYY-MM-DD)"
    )

    # Additional fields
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)

    # Relationships
    user: "User" = Relationship(back_populates="profile")
    site: "Site" = Relationship(back_populates="profile_sites")
