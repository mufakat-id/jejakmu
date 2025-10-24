import uuid

from sqlmodel import Session

from app.profiles.models import UserProfile
from app.profiles.repository import UserProfileRepository
from app.profiles.schema import UserProfileCreate, UserProfileUpdate
from app.repositories.user_profile_site_repository import UserProfileSiteRepository


class UserProfileService:
    """Service for user profile business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = UserProfileRepository(session)
        self.profile_site_repository = UserProfileSiteRepository(session)

    def create_profile(self, profile_in: UserProfileCreate) -> UserProfile:
        """Create a new profile"""
        # Business logic: Check if profile already exists for user
        existing = self.repository.get_by_user_id(profile_in.user_id)
        if existing:
            raise ValueError("Profile already exists for user")

        profile_dict = profile_in.model_dump()
        return self.repository.create(profile_dict)

    def get_profile(self, profile_id: uuid.UUID) -> UserProfile | None:
        """Get profile by ID"""
        return self.repository.get(profile_id)

    def get_profile_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        """Get profile by user ID"""
        return self.repository.get_by_user_id(user_id)

    def get_profiles(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[UserProfile], int]:
        """Get all profiles with count"""
        profiles = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return profiles, count

    def update_profile(
        self, db_profile: UserProfile, profile_in: UserProfileUpdate
    ) -> UserProfile:
        """Update an existing profile"""
        profile_data = profile_in.model_dump(exclude_unset=True)
        return self.repository.update(db_profile, profile_data)

    def delete_profile(self, profile_id: uuid.UUID) -> bool:
        """Delete profile by ID"""
        return self.repository.delete(profile_id)

    def assign_site_to_profile(
        self, profile_id: uuid.UUID, site_id: uuid.UUID, role_in_site: str | None = None
    ):
        """Assign a site to a profile"""
        # Verify profile exists
        profile = self.repository.get(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        return self.profile_site_repository.assign_site(
            profile_id, site_id, role_in_site
        )

    def remove_site_from_profile(
        self, profile_id: uuid.UUID, site_id: uuid.UUID
    ) -> bool:
        """Remove a site from a profile"""
        return self.profile_site_repository.remove_site(profile_id, site_id)

    def get_profile_sites(self, profile_id: uuid.UUID):
        """Get all sites for a profile"""
        return self.profile_site_repository.get_profile_sites_with_details(profile_id)
