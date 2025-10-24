import uuid

from sqlmodel import Session

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate
from app.users.models import Role
from app.users.repository import RoleRepository
from app.users.schema import RoleCreate, RoleUpdate


class RoleService:
    """Service for role business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = RoleRepository(session)

    def create_role(self, role_in: RoleCreate) -> Role:
        """Create a new role"""
        # Business logic: Check if role already exists
        existing = self.repository.get_by_name(role_in.name)
        if existing:
            raise ValueError(f"Role with name '{role_in.name}' already exists")

        role_dict = role_in.model_dump()
        return self.repository.create(role_dict)

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        """Get role by ID"""
        return self.repository.get(role_id)

    def get_role_by_name(self, name: str) -> Role | None:
        """Get role by name"""
        return self.repository.get_by_name(name)

    def get_roles(self, skip: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        """Get all roles with count"""
        roles = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return roles, count

    def get_active_roles(self) -> list[Role]:
        """Get all active roles"""
        return self.repository.get_active_roles()

    def update_role(self, db_role: Role, role_in: RoleUpdate) -> Role:
        """Update an existing role"""
        role_data = role_in.model_dump(exclude_unset=True)

        # Business logic: Check name uniqueness if being updated
        if "name" in role_data and role_data["name"] != db_role.name:
            existing = self.repository.get_by_name(role_data["name"])
            if existing:
                raise ValueError(f"Role with name '{role_data['name']}' already exists")

        return self.repository.update(db_role, role_data)

    def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete role by ID"""
        return self.repository.delete(role_id)


class UserService:
    """Service for user business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = UserRepository(session)

    def create_user(self, user_in: UserCreate) -> User:
        """Create a new user with hashed password"""
        user_dict = user_in.model_dump()
        password = user_in.password
        if password is None:
            password = uuid.uuid4().hex  # Generate a random password if none provided
        user_dict["hashed_password"] = get_password_hash(password)
        user_dict.pop("password", None)
        return self.repository.create(user_dict)

    def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get user by ID"""
        return self.repository.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return self.repository.get_by_email(email)

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Get all users with count"""
        users = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return users, count

    def update_user(self, db_user: User, user_in: UserUpdate) -> User:
        """Update user with optional password hashing"""
        user_data = user_in.model_dump(exclude_unset=True)
        if "password" in user_data:
            password = user_data.pop("password")
            user_data["hashed_password"] = get_password_hash(password)
        return self.repository.update(db_user, user_data)

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user by ID"""
        return self.repository.delete(user_id)

    def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password"""
        db_user = self.get_user_by_email(email)
        if not db_user:
            return None
        # OAuth users don't have password
        if not db_user.hashed_password:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user

    def check_email_exists(
        self, email: str, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        """Check if email already exists, optionally excluding a specific user"""
        existing_user = self.get_user_by_email(email)
        if not existing_user:
            return False
        if exclude_user_id and existing_user.id == exclude_user_id:
            return False
        return True

    def bulk_update_active_status(
        self, user_ids: list[uuid.UUID], is_active: bool
    ) -> tuple[int, list[uuid.UUID]]:
        """
        Bulk update is_active status for multiple users
        Returns (updated_count, failed_ids)
        """
        updated_count = 0
        failed_ids = []

        for user_id in user_ids:
            user = self.get_user_by_id(user_id)
            if user:
                user.is_active = is_active
                self.session.add(user)
                updated_count += 1
            else:
                failed_ids.append(user_id)

        if updated_count > 0:
            self.session.commit()

        return updated_count, failed_ids
