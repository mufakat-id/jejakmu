from sqlmodel import SQLModel

from app.auditlogs.models import AuditLog
from app.items.models import Item

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
from app.models.user_profile_site import UserProfileSite
from app.profiles.models import UserProfile
from app.sites.models import Site
from app.users.models import Role, User, UserRole

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
