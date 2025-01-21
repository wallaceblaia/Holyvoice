from app.crud.crud_user import user
from app.crud.youtube import youtube, youtube_playlist, youtube_video, youtube_access

__all__ = [
    "user",
    "youtube",
    "youtube_playlist",
    "youtube_video",
    "youtube_access",
]

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item) 