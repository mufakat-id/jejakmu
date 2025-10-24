from sqlmodel import SQLModel

from app.auditlogs.models import AuditLog
from app.items.models import Item
from app.models.role import Role

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
from app.sites.models import Site
from app.users.models import User

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
