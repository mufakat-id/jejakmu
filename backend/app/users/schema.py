import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import Field


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str | None = Field(min_length=8, max_length=40, default=None)
    is_superuser: bool = False


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Google OAuth schemas
class GoogleAuthRequest(BaseModel):
    code: str = Field(description="Authorization code from Google OAuth")


class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    is_superuser: bool

    model_config = {"from_attributes": True}


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class UserResponse(UserBase):
    id: uuid.UUID


class UserBulkUpdateActive(BaseModel):
    user_ids: list[uuid.UUID] = Field(
        min_length=1, description="List of user IDs to update"
    )
    is_active: bool = Field(description="New is_active status for all users")


class BulkUpdateResult(BaseModel):
    updated_count: int
    failed_ids: list[uuid.UUID] = []
    message: str
