import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep
from app.profiles.schema import (
    UserProfileCreate,
    UserProfilePublic,
    UserProfilesPublic,
    UserProfileUpdate,
    UserProfileWithSites,
)
from app.profiles.service import UserProfileService
from app.schemas.common import Message

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/", response_model=UserProfilesPublic)
def read_profiles(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all profiles.

    Only superusers can list all profiles.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = UserProfileService(session)
    profiles, count = service.get_profiles(skip=skip, limit=limit)
    return UserProfilesPublic(data=profiles, count=count)


@router.get("/me", response_model=UserProfileWithSites)
def read_my_profile(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user's profile with associated sites.
    """
    service = UserProfileService(session)
    profile = service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Get associated sites
    sites = service.get_profile_sites(profile.id)
    site_ids = [site.id for site in sites]

    return UserProfileWithSites(**profile.model_dump(), site_ids=site_ids)


@router.get("/{id}", response_model=UserProfilePublic)
def read_profile(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get profile by ID.

    Users can only view their own profile unless they are superusers.
    """
    service = UserProfileService(session)
    profile = service.get_profile(id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check permissions
    if profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return profile


@router.post("/", response_model=UserProfilePublic)
def create_profile(
    *, session: SessionDep, current_user: CurrentUser, profile_in: UserProfileCreate
) -> Any:
    """
    Create new profile.

    Users can only create their own profile.
    """
    # Check if user is creating their own profile or is superuser
    if profile_in.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = UserProfileService(session)
    try:
        profile = service.create_profile(profile_in)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id}", response_model=UserProfilePublic)
def update_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    profile_in: UserProfileUpdate,
) -> Any:
    """
    Update a profile.

    Users can only update their own profile.
    """
    service = UserProfileService(session)
    db_profile = service.get_profile(id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check permissions
    if db_profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_profile = service.update_profile(db_profile, profile_in)
    return updated_profile


@router.delete("/{id}", response_model=Message)
def delete_profile(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Delete a profile.

    Users can only delete their own profile.
    """
    service = UserProfileService(session)
    db_profile = service.get_profile(id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check permissions
    if db_profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = service.delete_profile(id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return Message(message="Profile deleted successfully")


@router.post("/{profile_id}/sites/{site_id}", response_model=Message)
def assign_site_to_profile(
    session: SessionDep,
    current_user: CurrentUser,
    profile_id: uuid.UUID,
    site_id: uuid.UUID,
    role_in_site: str | None = None,
) -> Any:
    """
    Assign a site to a profile.

    Users can only assign sites to their own profile unless they are superusers.
    """
    service = UserProfileService(session)
    profile = service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check permissions
    if profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        service.assign_site_to_profile(profile_id, site_id, role_in_site)
        return Message(message="Site assigned to profile successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{profile_id}/sites/{site_id}", response_model=Message)
def remove_site_from_profile(
    session: SessionDep,
    current_user: CurrentUser,
    profile_id: uuid.UUID,
    site_id: uuid.UUID,
) -> Any:
    """
    Remove a site from a profile.

    Users can only remove sites from their own profile unless they are superusers.
    """
    service = UserProfileService(session)
    profile = service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check permissions
    if profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = service.remove_site_from_profile(profile_id, site_id)
    if not success:
        raise HTTPException(status_code=404, detail="Site association not found")
    return Message(message="Site removed from profile successfully")
