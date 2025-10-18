import uuid

from sqlmodel import Session, func, select

from app.models import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item model with custom queries"""

    def __init__(self, session: Session):
        super().__init__(Item, session)

    def get_by_owner(
        self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Item]:
        """Get all items for a specific owner"""
        statement = (
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_by_owner(self, owner_id: uuid.UUID) -> int:
        """Count items for a specific owner"""
        statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        )
        return self.session.exec(statement).one()

    def delete_by_owner(self, owner_id: uuid.UUID) -> int:
        """Delete all items for a specific owner. Returns count of deleted items."""
        from sqlmodel import col, delete

        statement = delete(Item).where(col(Item.owner_id) == owner_id)
        result = self.session.exec(statement)
        self.session.commit()
        return result.rowcount  # type: ignore
