from sqlmodel import SQLModel

from app.models.audit import AuditLog
from app.models.item import Item
from app.models.role import Role
from app.models.site import Site
from app.models.user import User

# Import all CV models from single user_cv module
from app.models.user_cv import (  # noqa: E402
    CVCertification,
    CVEducation,
    CVFile,
    CVLanguage,
    CVProject,
    CVSkill,
    CVWorkExperience,
    UserCV,
)
from app.models.user_profile import UserProfile
from app.models.user_profile_site import UserProfileSite
from app.models.user_role import UserRole

__all__ = [
    "SQLModel",
    "User",
    "Item",
    "AuditLog",
    "Site",
    "Role",
    "UserRole",
    "UserProfile",
    "UserProfileSite",
    "UserCV",
    "CVFile",
    "CVEducation",
    "CVWorkExperience",
    "CVSkill",
    "CVCertification",
    "CVLanguage",
    "CVProject",
]
