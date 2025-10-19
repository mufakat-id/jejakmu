"""
Sites API endpoints
"""
import uuid

from fastapi import APIRouter, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep
from app.models.site import Site
from app.repositories import site as site_repository
from app.schemas.site import SiteCreate, SitePublic, SitesPublic, SiteUpdate

router = APIRouter()


@router.post("/", response_model=SitePublic)
def create_site(
    *, session: SessionDep, current_user: CurrentUser, site_in: SiteCreate
) -> Site:
    """
    Create new site. Only for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if domain already exists
    existing_site = site_repository.get_site_by_domain(
        session=session, domain=site_in.domain
    )
    if existing_site:
        raise HTTPException(
            status_code=400,
            detail=f"Site with domain {site_in.domain} already exists",
        )

    return site_repository.create_site(session=session, site_create=site_in)


@router.get("/", response_model=SitesPublic)
def read_sites(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> SitesPublic:
    """
    Retrieve sites. Only for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    sites = site_repository.get_sites(session=session, skip=skip, limit=limit)
    count = site_repository.get_sites_count(session=session)

    return SitesPublic(data=[SitePublic.model_validate(site) for site in sites], count=count)


@router.get("/current", response_model=SitePublic | None)
def get_current_site_endpoint(session: SessionDep) -> Site | None:
    """
    Get the current site based on request host.
    This endpoint is public to allow frontend to know which site they're on.
    """
    from app.core.sites import get_current_site

    return get_current_site()


@router.get("/{site_id}", response_model=SitePublic)
def read_site(
    session: SessionDep, current_user: CurrentUser, site_id: uuid.UUID
) -> Site:
    """
    Get site by ID. Only for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    site = site_repository.get_site_by_id(session=session, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return site


@router.patch("/{site_id}", response_model=SitePublic)
def update_site(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    site_id: uuid.UUID,
    site_in: SiteUpdate,
) -> Site:
    """
    Update a site. Only for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    site = site_repository.get_site_by_id(session=session, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # If updating domain, check if new domain already exists
    if site_in.domain and site_in.domain != site.domain:
        existing_site = site_repository.get_site_by_domain(
            session=session, domain=site_in.domain
        )
        if existing_site:
            raise HTTPException(
                status_code=400,
                detail=f"Site with domain {site_in.domain} already exists",
            )

    return site_repository.update_site(
        session=session, db_site=site, site_update=site_in
    )


@router.delete("/{site_id}")
def delete_site(
    session: SessionDep, current_user: CurrentUser, site_id: uuid.UUID
) -> dict[str, str]:
    """
    Delete a site. Only for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    site = site_repository.get_site_by_id(session=session, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Prevent deleting default site
    if site.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the default site. Set another site as default first.",
        )

    site_repository.delete_site(session=session, site_id=site_id)
    return {"message": "Site deleted successfully"}
