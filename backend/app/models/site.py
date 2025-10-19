import uuid
from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.audit import AuditMixin


class Site(SQLModel, AuditMixin, table=True):
    """
    Site model - inspired by Django's contrib.sites framework.
    Allows managing multiple sites/domains from a single application.

    Use cases:
    - Multi-tenancy support
    - Different domains for same application
    - Environment-specific URLs (dev, staging, production)
    - Generate correct absolute URLs based on current site
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    domain: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False, index=True)

    # Optional: Additional configuration per site
    settings: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    def __str__(self) -> str:
        return f"{self.name} ({self.domain})"
