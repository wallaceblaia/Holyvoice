from .crud_user import crud_user
from .crud_youtube import crud_youtube
from .crud_monitoring import crud_monitoring

__all__ = [
    "crud_user",
    "crud_youtube",
    "crud_monitoring"
]

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item) 