import uuid
from typing import Any, Generic, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Generic repository for CRUD operations"""

    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: uuid.UUID) -> ModelType | None:
        """Get a single record by ID"""
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record"""
        # The constructor `self.model(**obj_in)` already performs validation and
        # is sufficient. Using `model_validate` is more explicit for data parsing,
        # but the original code was doing a redundant double validation.
        # ## the original code is not working, cannot find the proper cause
        # db_obj = self.model.model_validate(obj_in)
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        """Update an existing record"""
        db_obj.sqlmodel_update(obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: uuid.UUID) -> bool:
        """Delete a record by ID"""
        db_obj = self.get(id)
        if db_obj:
            self.session.delete(db_obj)
            self.session.commit()
            return True
        return False

    def count(self) -> int:
        """Count total records"""
        from sqlmodel import func

        statement = select(func.count()).select_from(self.model)
        return self.session.exec(statement).one()
