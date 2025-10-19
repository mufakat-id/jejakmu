# User Roles & Profiles

Dokumentasi lengkap untuk fitur User Roles dan User Profiles dengan multiple site associations.

## 📋 Daftar Isi

- [Overview](#overview)
- [Arsitektur](#arsitektur)
- [Setup & Installation](#setup--installation)
- [Models](#models)
- [API Endpoints](#api-endpoints)
- [Penggunaan](#penggunaan)
- [Best Practices](#best-practices)

## Overview

Fitur ini menambahkan kemampuan untuk:

1. **Multiple Roles per User** - Setiap user bisa memiliki beberapa role (admin, editor, viewer, dll)
2. **User Profiles** - Extended user information (phone, address, bio, avatar, dll)
3. **Multiple Sites per Profile** - Setiap user profile bisa diasosiasikan dengan beberapa sites

### Use Cases

- **Role-Based Access Control (RBAC)** - Kontrol akses berdasarkan role
- **Multi-tenancy** - User bisa akses multiple sites dengan role berbeda
- **User Management** - Profile lengkap untuk setiap user
- **Site-specific Permissions** - User punya role berbeda di setiap site

## Arsitektur

### Database Schema

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│    User     │────────<│  UserRole    │>────────│     Role     │
└─────────────┘         └──────────────┘         └──────────────┘
      │
      │ 1:1
      │
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│ UserProfile │────────<│ProfileSite   │>────────│     Site     │
└─────────────┘         └──────────────┘         └──────────────┘
```

### Relationships

- **User ↔ Role**: Many-to-Many (via `user_role`)
- **User ↔ UserProfile**: One-to-One
- **UserProfile ↔ Site**: Many-to-Many (via `user_profile_site`)

## Setup & Installation

### 1. Migration Database

Models sudah dibuat, sekarang jalankan migration:

```bash
# Masuk ke container backend (jika menggunakan Docker)
docker compose exec backend bash

# Apply migration
alembic upgrade head
```

Atau jika development lokal:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

### 2. Seed Default Roles (Optional)

Buat file untuk seed default roles:

```python
# backend/app/initial_roles.py
from sqlmodel import Session, select

from app.core.db import engine
from app.models import Role


def create_default_roles() -> None:
    """Create default roles if they don't exist"""
    with Session(engine) as session:
        # Check if roles already exist
        statement = select(Role)
        existing_roles = session.exec(statement).first()

        if existing_roles:
            print("Roles already exist, skipping initialization")
            return

        # Create default roles
        default_roles = [
            Role(name="admin", description="Administrator with full access"),
            Role(name="editor", description="Can create and edit content"),
            Role(name="viewer", description="Read-only access"),
            Role(name="manager", description="Manage users and settings"),
        ]

        for role in default_roles:
            session.add(role)

        session.commit()
        print(f"Created {len(default_roles)} default roles")


if __name__ == "__main__":
    create_default_roles()
```

Jalankan:

```bash
python -m app.initial_roles
```

## Models

### 1. Role

Model untuk mendefinisikan roles dalam sistem.

```python
from app.models import Role

role = Role(
    name="editor",
    description="Content editor role",
    is_active=True
)
```

**Fields:**
- `id` (UUID): Primary key
- `name` (str): Unique role name
- `description` (str | None): Role description
- `is_active` (bool): Whether role is active
- `created_at`, `updated_at`: Audit fields

### 2. UserRole

Junction table untuk many-to-many User-Role relationship.

```python
from app.models import UserRole

user_role = UserRole(
    user_id=user.id,
    role_id=role.id,
    is_active=True
)
```

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `role_id` (UUID): Foreign key to Role
- `is_active` (bool): Whether assignment is active

### 3. UserProfile

Extended user information.

```python
from app.models import UserProfile

profile = UserProfile(
    user_id=user.id,
    phone="+628123456789",
    address="Jl. Example No. 123",
    bio="Software Engineer",
    avatar_url="https://example.com/avatar.jpg",
    city="Jakarta",
    country="Indonesia"
)
```

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Unique foreign key to User
- `phone` (str | None): Phone number
- `address` (str | None): Address
- `bio` (str | None): Bio/description
- `avatar_url` (str | None): Avatar image URL
- `date_of_birth` (str | None): Date of birth
- `city`, `country`, `postal_code`: Location fields

### 4. UserProfileSite

Junction table untuk many-to-many Profile-Site relationship.

```python
from app.models import UserProfileSite

profile_site = UserProfileSite(
    profile_id=profile.id,
    site_id=site.id,
    is_active=True,
    role_in_site="manager"  # Optional: site-specific role
)
```

**Fields:**
- `id` (UUID): Primary key
- `profile_id` (UUID): Foreign key to UserProfile
- `site_id` (UUID): Foreign key to Site
- `is_active` (bool): Whether association is active
- `role_in_site` (str | None): Site-specific role

## API Endpoints

### Roles Management

#### GET `/api/v1/roles/`
List all roles (authenticated users).

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "admin",
      "description": "Administrator",
      "is_active": true
    }
  ],
  "count": 1
}
```

#### POST `/api/v1/roles/`
Create new role (superuser only).

**Request:**
```json
{
  "name": "moderator",
  "description": "Content moderator",
  "is_active": true
}
```

#### PATCH `/api/v1/roles/{id}`
Update role (superuser only).

#### DELETE `/api/v1/roles/{id}`
Delete role (superuser only).

### User Roles Management

#### POST `/api/v1/users/{user_id}/roles/{role_id}`
Assign role to user.

**Permissions:** User can assign to self, or superuser can assign to anyone.

**Response:**
```json
{
  "message": "Role 'editor' assigned to user successfully"
}
```

#### DELETE `/api/v1/users/{user_id}/roles/{role_id}`
Remove role from user.

#### GET `/api/v1/users/{user_id}/roles`
Get all roles for a user.

**Response:**
```json
{
  "user_id": "uuid",
  "roles": [
    {
      "id": "uuid",
      "name": "admin",
      "description": "Administrator"
    }
  ]
}
```

#### GET `/api/v1/users/{user_id}/roles/{role_name}/check`
Check if user has specific role.

**Response:**
```json
{
  "user_id": "uuid",
  "role_name": "admin",
  "has_role": true
}
```

### User Profiles Management

#### GET `/api/v1/profiles/me`
Get current user's profile with associated sites.

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "phone": "+628123456789",
  "address": "Jl. Example",
  "bio": "Software Engineer",
  "avatar_url": "https://example.com/avatar.jpg",
  "city": "Jakarta",
  "country": "Indonesia",
  "site_ids": ["site-uuid-1", "site-uuid-2"]
}
```

#### POST `/api/v1/profiles/`
Create new profile.

**Request:**
```json
{
  "user_id": "uuid",
  "phone": "+628123456789",
  "address": "Jl. Example No. 123",
  "bio": "Software Engineer",
  "city": "Jakarta",
  "country": "Indonesia"
}
```

#### PATCH `/api/v1/profiles/{id}`
Update profile.

**Request:**
```json
{
  "phone": "+628987654321",
  "bio": "Senior Software Engineer"
}
```

#### POST `/api/v1/profiles/{profile_id}/sites/{site_id}`
Assign site to profile.

**Query Params:**
- `role_in_site` (optional): Site-specific role

**Response:**
```json
{
  "message": "Site assigned to profile successfully"
}
```

#### DELETE `/api/v1/profiles/{profile_id}/sites/{site_id}`
Remove site from profile.

## Penggunaan

### 1. Assign Role ke User

```python
from app.repositories.user_role_repository import UserRoleRepository
from app.repositories.role_repository import RoleRepository

# Get repositories
role_repo = RoleRepository(session)
user_role_repo = UserRoleRepository(session)

# Get role
admin_role = role_repo.get_by_name("admin")

# Assign role to user
user_role_repo.assign_role(user_id, admin_role.id)
```

### 2. Check User Role

```python
from app.repositories.user_role_repository import UserRoleRepository

user_role_repo = UserRoleRepository(session)

# Check if user has role
is_admin = user_role_repo.has_role(user_id, "admin")

if is_admin:
    # Allow admin actions
    pass
```

### 3. Get User's Roles

```python
from app.repositories.user_role_repository import UserRoleRepository

user_role_repo = UserRoleRepository(session)

# Get all roles for user
roles = user_role_repo.get_user_roles_with_details(user_id)

for role in roles:
    print(f"User has role: {role.name}")
```

### 4. Create User Profile

```python
from app.services.user_profile_service import UserProfileService
from app.schemas.user_profile import UserProfileCreate

service = UserProfileService(session)

profile_data = UserProfileCreate(
    user_id=user.id,
    phone="+628123456789",
    address="Jl. Example",
    city="Jakarta",
    country="Indonesia"
)

profile = service.create_profile(profile_data)
```

### 5. Assign Sites to Profile

```python
from app.services.user_profile_service import UserProfileService

service = UserProfileService(session)

# Assign site with optional role
service.assign_site_to_profile(
    profile_id=profile.id,
    site_id=site.id,
    role_in_site="manager"
)
```

### 6. Role-Based Authorization Decorator

Buat custom decorator untuk role checking:

```python
# app/core/authorization.py
from functools import wraps
from fastapi import HTTPException

from app.repositories.user_role_repository import UserRoleRepository

def require_role(role_name: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs
            current_user = kwargs.get("current_user")
            session = kwargs.get("session")

            if not current_user or not session:
                raise HTTPException(status_code=401, detail="Not authenticated")

            # Check role
            user_role_repo = UserRoleRepository(session)
            has_role = user_role_repo.has_role(current_user.id, role_name)

            if not has_role and not current_user.is_superuser:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires '{role_name}' role"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

Penggunaan:

```python
from app.core.authorization import require_role

@router.delete("/sensitive-data/{id}")
@require_role("admin")
def delete_sensitive_data(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
):
    # Only users with 'admin' role can access
    pass
```

## Best Practices

### 1. Role Naming Convention

Gunakan lowercase dan singular:
- ✅ `admin`, `editor`, `viewer`
- ❌ `ADMIN`, `Editors`, `view-only`

### 2. Profile Creation

Buat profile otomatis saat user signup:

```python
@router.post("/signup", response_model=UserPublic)
def signup(session: SessionDep, user_in: UserRegister):
    # Create user
    user = create_user(session, user_in)

    # Auto-create profile
    profile_service = UserProfileService(session)
    profile_service.create_profile(UserProfileCreate(
        user_id=user.id,
        # Set defaults if needed
    ))

    return user
```

### 3. Site Assignment

Assign default site saat create profile:

```python
from app.core.sites import get_current_site

def create_profile_with_site(session, user_id):
    # Create profile
    profile = profile_service.create_profile(...)

    # Assign current site
    current_site = get_current_site()
    if current_site:
        profile_service.assign_site_to_profile(
            profile.id,
            current_site.id
        )
```

### 4. Hierarchical Roles

Jika perlu role hierarchy, tambahkan logic di service layer:

```python
ROLE_HIERARCHY = {
    "admin": ["editor", "viewer"],
    "editor": ["viewer"],
    "viewer": []
}

def user_has_role_or_higher(user_id: uuid.UUID, role_name: str) -> bool:
    """Check if user has role or higher role"""
    user_roles = get_user_roles(user_id)

    for user_role in user_roles:
        if user_role.name == role_name:
            return True

        # Check hierarchy
        implied_roles = ROLE_HIERARCHY.get(user_role.name, [])
        if role_name in implied_roles:
            return True

    return False
```

### 5. Soft Delete Roles

Gunakan `is_active` field daripada delete:

```python
# Soft delete
def deactivate_role(role_id: uuid.UUID):
    role = role_repo.get(role_id)
    role.is_active = False
    role_repo.update(role, {"is_active": False})
```

## Testing

### Test Role Assignment

```python
def test_assign_role_to_user(session: Session):
    # Create user and role
    user = create_test_user(session)
    role = Role(name="editor", is_active=True)
    session.add(role)
    session.commit()

    # Assign role
    user_role_repo = UserRoleRepository(session)
    user_role_repo.assign_role(user.id, role.id)

    # Verify
    assert user_role_repo.has_role(user.id, "editor")
```

### Test Profile Creation

```python
def test_create_profile(session: Session):
    user = create_test_user(session)

    service = UserProfileService(session)
    profile = service.create_profile(UserProfileCreate(
        user_id=user.id,
        phone="+628123456789"
    ))

    assert profile.user_id == user.id
    assert profile.phone == "+628123456789"
```

## Troubleshooting

### "Profile already exists for user"

**Problem:** Mencoba create profile untuk user yang sudah punya profile.

**Solution:** Check terlebih dahulu atau gunakan update jika sudah ada.

### "Role assignment not found"

**Problem:** Mencoba remove role yang tidak di-assign.

**Solution:** Check role assignment sebelum remove.

### Permission Denied

**Problem:** User tidak punya permission untuk action tertentu.

**Solution:**
1. Pastikan user punya role yang tepat
2. Check `is_active` status pada role assignment
3. Verify user authentication

## Migration Rollback

Jika perlu rollback migration:

```bash
# Check current version
alembic current

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

## Referensi

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Created:** 2025-10-19
**Version:** 1.0.0
