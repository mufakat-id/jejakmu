import uuid

from sqlmodel import Session

from app.models import Item
from app.repositories import ItemRepository
from app.schemas import ItemCreate, ItemUpdate


class ItemService:
    """Service for item business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = ItemRepository(session)

    def create_item(self, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        """Create a new item for a specific owner"""
        item_dict = item_in.model_dump()
        item_dict["owner_id"] = owner_id
        return self.repository.create(item_dict)

    def get_item_by_id(self, item_id: uuid.UUID) -> Item | None:
        """Get item by ID"""
        return self.repository.get(item_id)

    def get_items(self, skip: int = 0, limit: int = 100) -> tuple[list[Item], int]:
        """Get all items with count"""
        items = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return items, count

    def get_items_by_owner(
        self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Item], int]:
        """Get items for a specific owner with count"""
        items = self.repository.get_by_owner(owner_id, skip=skip, limit=limit)
        count = self.repository.count_by_owner(owner_id)
        return items, count

    def update_item(self, db_item: Item, item_in: ItemUpdate) -> Item:
        """Update an existing item"""
        item_data = item_in.model_dump(exclude_unset=True)
        return self.repository.update(db_item, item_data)

    def delete_item(self, item_id: uuid.UUID) -> bool:
        """Delete item by ID"""
        return self.repository.delete(item_id)

    def delete_items_by_owner(self, owner_id: uuid.UUID) -> int:
        """Delete all items for a specific owner. Returns count of deleted items."""
        return self.repository.delete_by_owner(owner_id)

    def check_item_ownership(self, item: Item, user_id: uuid.UUID) -> bool:
        """Check if item belongs to user"""
        return item.owner_id == user_id
