from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.youtube import YoutubeChannel, YoutubePlaylist, YoutubeVideo, YoutubeChannelAccess
from app.schemas.youtube import (
    YoutubeChannelCreate,
    YoutubeChannelUpdate,
    YoutubePlaylistCreate,
    YoutubeVideoCreate,
    YoutubeChannelAccessCreate,
)


class CRUDYoutubeChannel(CRUDBase[YoutubeChannel, YoutubeChannelCreate, YoutubeChannelUpdate]):
    def create_channel(self, db: Session, *, obj_in: Dict[str, Any]) -> YoutubeChannel:
        db_obj = YoutubeChannel(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_url(self, db: Session, *, channel_url: str) -> Optional[YoutubeChannel]:
        """
        Obtém um canal pela URL.
        """
        return db.query(YoutubeChannel).filter(YoutubeChannel.channel_url == channel_url).first()
    
    def get_by_channel_id(self, db: Session, *, channel_id: str) -> Optional[YoutubeChannel]:
        """
        Obtém um canal pelo ID do YouTube.
        """
        return db.query(YoutubeChannel).filter(YoutubeChannel.channel_id == channel_id).first()

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeChannel]:
        """
        Obtém todos os canais que o usuário tem acesso.
        """
        return (
            db.query(YoutubeChannel)
            .join(YoutubeChannelAccess)
            .filter(
                YoutubeChannelAccess.user_id == user_id,
                YoutubeChannelAccess.can_view == True
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def user_has_access(self, db: Session, *, user_id: int, channel_id: int) -> bool:
        access = (
            db.query(YoutubeChannelAccess)
            .filter(
                and_(
                    YoutubeChannelAccess.user_id == user_id,
                    YoutubeChannelAccess.channel_id == channel_id,
                    YoutubeChannelAccess.can_view == True,
                )
            )
            .first()
        )
        return bool(access)

    def user_can_edit(self, db: Session, *, user_id: int, channel_id: int) -> bool:
        access = (
            db.query(YoutubeChannelAccess)
            .filter(
                and_(
                    YoutubeChannelAccess.user_id == user_id,
                    YoutubeChannelAccess.channel_id == channel_id,
                    YoutubeChannelAccess.can_edit == True,
                )
            )
            .first()
        )
        return bool(access)

    def user_can_delete(self, db: Session, *, user_id: int, channel_id: int) -> bool:
        access = (
            db.query(YoutubeChannelAccess)
            .filter(
                and_(
                    YoutubeChannelAccess.user_id == user_id,
                    YoutubeChannelAccess.channel_id == channel_id,
                    YoutubeChannelAccess.can_delete == True,
                )
            )
            .first()
        )
        return bool(access)


class CRUDYoutubePlaylist(CRUDBase[YoutubePlaylist, YoutubePlaylistCreate, YoutubePlaylistCreate]):
    def create_with_channel(
        self, db: Session, *, obj_in: YoutubePlaylistCreate, channel_id: int
    ) -> YoutubePlaylist:
        db_obj = YoutubePlaylist(
            **obj_in.dict(),
            channel_id=channel_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_playlist_id(self, db: Session, *, playlist_id: str) -> Optional[YoutubePlaylist]:
        """
        Obtém uma playlist pelo ID do YouTube.
        """
        return db.query(YoutubePlaylist).filter(YoutubePlaylist.playlist_id == playlist_id).first()
    
    def get_multi_by_channel(
        self, db: Session, *, channel_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubePlaylist]:
        """
        Obtém todas as playlists de um canal.
        """
        return (
            db.query(YoutubePlaylist)
            .filter(YoutubePlaylist.channel_id == channel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDYoutubeVideo(CRUDBase[YoutubeVideo, YoutubeVideoCreate, YoutubeVideoCreate]):
    def create_with_channel(
        self, db: Session, *, obj_in: YoutubeVideoCreate, channel_id: int
    ) -> YoutubeVideo:
        db_obj = YoutubeVideo(
            **obj_in.dict(),
            channel_id=channel_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_video_id(self, db: Session, *, video_id: str) -> Optional[YoutubeVideo]:
        """
        Obtém um vídeo pelo ID do YouTube.
        """
        return db.query(YoutubeVideo).filter(YoutubeVideo.video_id == video_id).first()
    
    def get_multi_by_channel(
        self, db: Session, *, channel_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeVideo]:
        """
        Obtém todos os vídeos de um canal.
        """
        return (
            db.query(YoutubeVideo)
            .filter(YoutubeVideo.channel_id == channel_id)
            .order_by(YoutubeVideo.published_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi_by_playlist(
        self, db: Session, *, playlist_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeVideo]:
        """
        Obtém todos os vídeos de uma playlist.
        """
        return (
            db.query(YoutubeVideo)
            .filter(YoutubeVideo.playlist_id == playlist_id)
            .order_by(YoutubeVideo.published_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDYoutubeAccess(CRUDBase[YoutubeChannelAccess, YoutubeChannelAccessCreate, YoutubeChannelAccessCreate]):
    def create_access(
        self, db: Session, *, obj_in: Dict[str, Any]
    ) -> YoutubeChannelAccess:
        db_obj = YoutubeChannelAccess(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_and_channel(
        self, db: Session, *, user_id: int, channel_id: int
    ) -> Optional[YoutubeChannelAccess]:
        """
        Obtém o registro de acesso de um usuário a um canal.
        """
        return (
            db.query(YoutubeChannelAccess)
            .filter(
                YoutubeChannelAccess.user_id == user_id,
                YoutubeChannelAccess.channel_id == channel_id
            )
            .first()
        )
    
    def get_users_with_access(
        self, db: Session, *, channel_id: int, skip: int = 0, limit: int = 100
    ) -> List[YoutubeChannelAccess]:
        """
        Obtém todos os usuários que têm acesso a um canal.
        """
        return (
            db.query(YoutubeChannelAccess)
            .filter(YoutubeChannelAccess.channel_id == channel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


youtube = CRUDYoutubeChannel(YoutubeChannel)
youtube_playlist = CRUDYoutubePlaylist(YoutubePlaylist)
youtube_video = CRUDYoutubeVideo(YoutubeVideo)
youtube_access = CRUDYoutubeAccess(YoutubeChannelAccess) 