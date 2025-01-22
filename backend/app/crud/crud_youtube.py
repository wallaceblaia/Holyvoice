from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.youtube import YoutubeChannel, YoutubeVideo, YoutubeChannelAccess
from app.schemas.youtube import (
    YoutubeChannelCreate as ChannelCreate,
    YoutubeChannelUpdate as ChannelUpdate,
    YoutubeVideoCreate as VideoCreate,
    YoutubeVideoUpdate as VideoUpdate,
    YoutubeChannelAccessCreate
)
from app import models, schemas


class CRUDYoutube(CRUDBase[YoutubeChannel, ChannelCreate, ChannelUpdate]):
    def __init__(self):
        super().__init__(model=YoutubeChannel)

    def get_channel(self, db: Session, *, id: int) -> Optional[YoutubeChannel]:
        return db.query(YoutubeChannel).filter(YoutubeChannel.id == id).first()

    def get_channel_by_youtube_id(self, db: Session, *, youtube_id: str) -> Optional[YoutubeChannel]:
        return db.query(YoutubeChannel).filter(YoutubeChannel.youtube_id == youtube_id).first()

    def get_channels_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeChannel]:
        """
        Obtém todos os canais que o usuário tem acesso.
        """
        return (
            db.query(YoutubeChannel)
            .join(YoutubeChannelAccess, YoutubeChannel.id == YoutubeChannelAccess.channel_id)
            .filter(
                YoutubeChannelAccess.user_id == user_id,
                YoutubeChannelAccess.can_view == True
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_video(self, db: Session, *, id: int) -> Optional[YoutubeVideo]:
        return db.query(YoutubeVideo).filter(YoutubeVideo.id == id).first()

    def get_video_by_youtube_id(
        self, db: Session, *, youtube_id: str, channel_id: int
    ) -> Optional[YoutubeVideo]:
        return (
            db.query(YoutubeVideo)
            .filter(
                YoutubeVideo.video_id == youtube_id,
                YoutubeVideo.channel_id == channel_id
            )
            .first()
        )

    def get_videos_by_ids(
        self, db: Session, *, video_ids: List[int], channel_id: int
    ) -> List[YoutubeVideo]:
        return (
            db.query(YoutubeVideo)
            .filter(
                YoutubeVideo.id.in_(video_ids),
                YoutubeVideo.channel_id == channel_id
            )
            .all()
        )

    def get_videos_by_channel(
        self, db: Session, *, channel_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeVideo]:
        return (
            db.query(YoutubeVideo)
            .filter(YoutubeVideo.channel_id == channel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_video(
        self, db: Session, *, obj_in: VideoCreate, channel_id: int
    ) -> YoutubeVideo:
        db_obj = YoutubeVideo(
            channel_id=channel_id,
            video_id=obj_in.video_id,
            title=obj_in.title,
            thumbnail_url=obj_in.thumbnail_url,
            published_at=obj_in.published_at,
            is_live=obj_in.is_live
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_video(
        self, db: Session, *, db_obj: YoutubeVideo, obj_in: VideoUpdate
    ) -> YoutubeVideo:
        update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def user_can_access_channel(
        self, db: Session, *, user_id: int, channel_id: int
    ) -> bool:
        access = (
            db.query(YoutubeChannelAccess)
            .filter(
                YoutubeChannelAccess.user_id == user_id,
                YoutubeChannelAccess.channel_id == channel_id,
                YoutubeChannelAccess.can_view == True
            )
            .first()
        )
        return access is not None

    def create_access(
        self,
        db: Session,
        *,
        obj_in: YoutubeChannelAccessCreate
    ) -> YoutubeChannelAccess:
        """
        Cria um novo registro de acesso a um canal.
        """
        db_obj = YoutubeChannelAccess(
            channel_id=obj_in.channel_id,
            user_id=obj_in.user_id,
            can_view=True,
            can_edit=obj_in.can_edit if hasattr(obj_in, 'can_edit') else False,
            can_delete=obj_in.can_delete if hasattr(obj_in, 'can_delete') else False,
            created_by=obj_in.created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_youtube = CRUDYoutube() 