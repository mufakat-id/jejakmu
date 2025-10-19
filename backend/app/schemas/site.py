"""
Site schemas for API requests and responses
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SiteBase(BaseModel):
    """Base schema for Site"""
    domain: str = Field(..., max_length=255, description="Domain name (e.g., example.com)")
    name: str = Field(..., max_length=255, description="Human-readable site name")
    is_active: bool = Field(default=True, description="Whether the site is active")
    is_default: bool = Field(default=False, description="Whether this is the default site")
    settings: dict | None = Field(default=None, description="Additional site-specific settings")


class SiteCreate(SiteBase):
    """Schema for creating a new site"""
    pass


class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    domain: str | None = None
    name: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None
    settings: dict | None = None


class SitePublic(SiteBase):
    """Public schema for Site"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SitesPublic(BaseModel):
    """Schema for list of sites"""
    data: list[SitePublic]
    count: int

