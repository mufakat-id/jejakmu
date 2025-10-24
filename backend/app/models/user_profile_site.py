import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.profiles.models import UserProfile
    from app.sites.models import Site


class UserProfileSite(SQLModel, AuditMixin, table=True):
    """
    Junction table for many-to-many relationship between UserProfile and Site.
    Allows one user profile to be associated with multiple sites.
    """

    __tablename__ = "user_profile_site"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    profile_id: uuid.UUID = Field(foreign_key="user_profile.id", index=True)
    site_id: uuid.UUID = Field(foreign_key="site.id", index=True)

    # Optional: Add extra fields for junction table
    is_active: bool = Field(
        default=True, description="Whether this site association is active"
    )
    role_in_site: str | None = Field(
        default=None, max_length=100, description="Specific role for this site"
    )

    # Relationships
    profile: "UserProfile" = Relationship(back_populates="profile_sites")
    site: "Site" = Relationship(back_populates="profile_sites")
