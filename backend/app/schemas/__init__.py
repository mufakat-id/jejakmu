from app.auditlogs.schema import AuditLogListResponse, AuditLogResponse
from app.items.schema import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.schemas.base import (
    BaseResponse,
    CreatedResponse,
    ListResponse,
    UpdateDeleteResponse,
)
from app.schemas.common import (
    GoogleAuthCodeRequest,
    Message,
    OAuthAccessDenied,
    Token,
    TokenPayload,
    TokenWithRefresh,
)
from app.users.schema import (
    BulkUpdateResult,
    GoogleAuthRequest,
    GoogleAuthResponse,
    NewPassword,
    RoleCreate,
    RolePublic,
    RolesPublic,
    RoleUpdate,
    UpdatePassword,
    UserBulkUpdateActive,
    UserCreate,
    UserPublic,
    UserRegister,
    UserResponse,
    UserRoleCreate,
    UserRolePublic,
    UserRolesPublic,
    UserRoleUpdate,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

__all__ = [
    # Common
    "GoogleAuthCodeRequest",
    "Message",
    "OAuthAccessDenied",
    "Token",
    "TokenPayload",
    "TokenWithRefresh",
    # Response
    "BaseResponse",
    "CreatedResponse",
    "ListResponse",
    "UpdateDeleteResponse",
    # Role
    "RoleCreate",
    "RolePublic",
    "RolesPublic",
    "RoleUpdate",
    # UserRole
    "UserRoleCreate",
    "UserRolePublic",
    "UserRolesPublic",
    "UserRoleUpdate",
    # User
    "BulkUpdateResult",
    "UserBulkUpdateActive",
    "UserCreate",
    "UserPublic",
    "UsersPublic",
    "UserUpdate",
    "UserUpdateMe",
    "UserRegister",
    "UpdatePassword",
    "NewPassword",
    "UserResponse",
    # Item
    "ItemCreate",
    "ItemPublic",
    "ItemsPublic",
    "ItemUpdate",
    # Audit
    "AuditLogResponse",
    "AuditLogListResponse",
    # Google Auth
    "GoogleAuthRequest",
    "GoogleAuthResponse",
]
