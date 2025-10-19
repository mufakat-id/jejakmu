import uuid

from sqlmodel import Field, SQLModel


# Base schema - shared properties
class RoleBase(SQLModel):
    name: str = Field(min_length=1, max_length=50, description="Role name")
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


# Create request
class RoleCreate(RoleBase):
    pass


# Update request
class RoleUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    is_active: bool | None = None


# Public response
class RolePublic(RoleBase):
    id: uuid.UUID


# List response
class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int
