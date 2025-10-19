import uuid
from sqlmodel import Session, select

from app.models.user_profile_site import UserProfileSite
from app.models.site import Site
from app.repositories.base import BaseRepository


class UserProfileSiteRepository(BaseRepository[UserProfileSite]):
    """Repository for UserProfileSite-specific database operations"""

    def __init__(self, session: Session):
        super().__init__(UserProfileSite, session)

    def get_by_profile_id(self, profile_id: uuid.UUID) -> list[UserProfileSite]:
        """Get all site associations for a specific profile"""
        statement = select(UserProfileSite).where(UserProfileSite.profile_id == profile_id)
        return list(self.session.exec(statement).all())

    def get_profile_sites_with_details(self, profile_id: uuid.UUID) -> list[Site]:
        """Get all site objects for a specific profile"""
        statement = (
            select(Site)
            .join(UserProfileSite, UserProfileSite.site_id == Site.id)
            .where(UserProfileSite.profile_id == profile_id)
            .where(UserProfileSite.is_active == True)
        )
        return list(self.session.exec(statement).all())

    def assign_site(self, profile_id: uuid.UUID, site_id: uuid.UUID, role_in_site: str | None = None) -> UserProfileSite:
        """Assign a site to a profile"""
        # Check if already exists
        statement = select(UserProfileSite).where(
            UserProfileSite.profile_id == profile_id,
            UserProfileSite.site_id == site_id
        )
        existing = self.session.exec(statement).first()

        if existing:
            # Update if exists
            if not existing.is_active:
                existing.is_active = True
            if role_in_site:
                existing.role_in_site = role_in_site
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing

        # Create new
        profile_site = UserProfileSite(
            profile_id=profile_id,
            site_id=site_id,
            role_in_site=role_in_site
        )
        self.session.add(profile_site)
        self.session.commit()
        self.session.refresh(profile_site)
        return profile_site

    def remove_site(self, profile_id: uuid.UUID, site_id: uuid.UUID) -> bool:
        """Remove a site from a profile"""
        statement = select(UserProfileSite).where(
            UserProfileSite.profile_id == profile_id,
            UserProfileSite.site_id == site_id
        )
        profile_site = self.session.exec(statement).first()

        if profile_site:
            self.session.delete(profile_site)
            self.session.commit()
            return True
        return False

    def has_site_access(self, profile_id: uuid.UUID, site_id: uuid.UUID) -> bool:
        """Check if profile has access to a specific site"""
        statement = select(UserProfileSite).where(
            UserProfileSite.profile_id == profile_id,
            UserProfileSite.site_id == site_id,
            UserProfileSite.is_active == True
        )
        return self.session.exec(statement).first() is not None

