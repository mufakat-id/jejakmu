import uuid

from sqlmodel import Field, SQLModel


# Base schema - shared properties
class UserProfileBase(SQLModel):
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=500)
    date_of_birth: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)


# Create request
class UserProfileCreate(UserProfileBase):
    user_id: uuid.UUID


# Update request
class UserProfileUpdate(UserProfileBase):
    pass


# Public response
class UserProfilePublic(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID


# Profile with site IDs
class UserProfileWithSites(UserProfilePublic):
    site_ids: list[uuid.UUID] = Field(
        default_factory=list, description="List of associated site IDs"
    )


# List response
class UserProfilesPublic(SQLModel):
    data: list[UserProfilePublic]
    count: int
