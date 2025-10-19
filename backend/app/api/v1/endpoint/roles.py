import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RolePublic, RolesPublic, RoleUpdate
from app.schemas.common import Message

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=RolesPublic)
def read_roles(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all roles.
    """
    service = RoleService(session)
    roles, count = service.get_roles(skip=skip, limit=limit)
    return RolesPublic(data=roles, count=count)


@router.get("/{id}", response_model=RolePublic)
def read_role(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get role by ID.
    """
    service = RoleService(session)
    role = service.get_role(id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RolePublic)
def create_role(
    *, session: SessionDep, current_user: CurrentUser, role_in: RoleCreate
) -> Any:
    """
    Create new role.

    Only superusers can create roles.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = RoleService(session)
    try:
        role = service.create_role(role_in)
        return role
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id}", response_model=RolePublic)
def update_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    role_in: RoleUpdate,
) -> Any:
    """
    Update a role.

    Only superusers can update roles.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = RoleService(session)
    db_role = service.get_role(id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        updated_role = service.update_role(db_role, role_in)
        return updated_role
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", response_model=Message)
def delete_role(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Delete a role.

    Only superusers can delete roles.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = RoleService(session)
    success = service.delete_role(id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return Message(message="Role deleted successfully")

