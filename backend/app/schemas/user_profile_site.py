import uuid
from sqlmodel import SQLModel, Field


# Base schema - shared properties
class UserProfileSiteBase(SQLModel):
    profile_id: uuid.UUID
    site_id: uuid.UUID
    is_active: bool = Field(default=True)
    role_in_site: str | None = Field(default=None, max_length=100)


# Create request
class UserProfileSiteCreate(UserProfileSiteBase):
    pass


# Update request
class UserProfileSiteUpdate(SQLModel):
    is_active: bool | None = None
    role_in_site: str | None = None


# Public response
class UserProfileSitePublic(UserProfileSiteBase):
    id: uuid.UUID


# List response
class UserProfileSitesPublic(SQLModel):
    data: list[UserProfileSitePublic]
    count: int

