import uuid

from sqlmodel import Field, SQLModel


# Base schema - shared properties
class UserRoleBase(SQLModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    is_active: bool = Field(default=True)


# Create request
class UserRoleCreate(UserRoleBase):
    pass


# Update request
class UserRoleUpdate(SQLModel):
    is_active: bool | None = None


# Public response
class UserRolePublic(UserRoleBase):
    id: uuid.UUID


# List response
class UserRolesPublic(SQLModel):
    data: list[UserRolePublic]
    count: int
