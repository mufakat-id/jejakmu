import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep
from app.users.repository import RoleRepository, UserRoleRepository
from app.schemas.common import Message

router = APIRouter(prefix="/users", tags=["user-roles"])


@router.post("/{user_id}/roles/{role_id}", response_model=Message)
def assign_role_to_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> Any:
    """
    Assign a role to a user.

    Users can only assign roles to themselves unless they are superusers.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Verify role exists
    role_repo = RoleRepository(session)
    role = role_repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user_role_repo = UserRoleRepository(session)
    user_role_repo.assign_role(user_id, role_id)

    return Message(message=f"Role '{role.name}' assigned to user successfully")


@router.delete("/{user_id}/roles/{role_id}", response_model=Message)
def remove_role_from_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> Any:
    """
    Remove a role from a user.

    Users can only remove roles from themselves unless they are superusers.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_role_repo = UserRoleRepository(session)
    success = user_role_repo.remove_role(user_id, role_id)

    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")

    return Message(message="Role removed from user successfully")


@router.get("/{user_id}/roles")
def get_user_roles(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
) -> Any:
    """
    Get all roles for a specific user.

    Users can only view their own roles unless they are superusers.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_role_repo = UserRoleRepository(session)
    roles = user_role_repo.get_user_roles_with_details(user_id)

    return {
        "user_id": user_id,
        "roles": [
            {"id": role.id, "name": role.name, "description": role.description}
            for role in roles
        ],
    }


@router.get("/{user_id}/roles/{role_name}/check")
def check_user_has_role(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    role_name: str,
) -> Any:
    """
    Check if user has a specific role.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_role_repo = UserRoleRepository(session)
    has_role = user_role_repo.has_role(user_id, role_name)

    return {"user_id": user_id, "role_name": role_name, "has_role": has_role}
