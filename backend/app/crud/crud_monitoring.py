from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.monitoring import (
    YoutubeMonitoring,
    MonitoringVideo,
    MonitoringStatus,
    VideoProcessingStatus,
    MonitoringPlaylist
)
from app.models.youtube import YoutubeVideo, YoutubeChannel
from app.schemas.monitoring import MonitoringCreate, MonitoringUpdate


class CRUDMonitoring(CRUDBase[YoutubeMonitoring, MonitoringCreate, MonitoringUpdate]):
    def __init__(self):
        super().__init__(model=YoutubeMonitoring)

    def get_multi_with_details(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[MonitoringStatus] = None
    ) -> List[YoutubeMonitoring]:
        query = (
            db.query(
                YoutubeMonitoring,
                YoutubeChannel.channel_name,
                YoutubeChannel.avatar_image,
                func.count(MonitoringVideo.id).label('total_videos'),
                func.count(case(
                    (MonitoringVideo.status == VideoProcessingStatus.completed, 1),
                    else_=None
                )).label('processed_videos')
            )
            .join(YoutubeChannel, YoutubeMonitoring.channel_id == YoutubeChannel.id)
            .outerjoin(MonitoringVideo, YoutubeMonitoring.id == MonitoringVideo.monitoring_id)
            .filter(YoutubeMonitoring.created_by == user_id)
            .group_by(YoutubeMonitoring.id, YoutubeChannel.channel_name, YoutubeChannel.avatar_image)
        )
        
        if status:
            query = query.filter(YoutubeMonitoring.status == status)
        
        results = query.offset(skip).limit(limit).all()
        
        # Converte os resultados para objetos YoutubeMonitoring com os campos adicionais
        monitorings = []
        for result in results:
            monitoring = result[0]
            monitoring.channel_name = result[1]
            monitoring.channel_avatar = result[2]
            monitoring.total_videos = result[3]
            monitoring.processed_videos = result[4]
            monitorings.append(monitoring)
            
        return monitorings

    def get_with_details(self, db: Session, *, id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna um monitoramento com detalhes do canal e estatísticas.
        """
        monitoring = db.query(YoutubeMonitoring).filter(YoutubeMonitoring.id == id).first()
        if not monitoring:
            return None

        # Obtém o canal
        channel = db.query(YoutubeChannel).filter(YoutubeChannel.id == monitoring.channel_id).first()
        if not channel:
            return None

        # Obtém os vídeos e calcula estatísticas
        total_videos = db.query(MonitoringVideo).filter(
            MonitoringVideo.monitoring_id == monitoring.id
        ).count()

        processed_videos = db.query(MonitoringVideo).filter(
            MonitoringVideo.monitoring_id == monitoring.id,
            MonitoringVideo.status == VideoProcessingStatus.completed
        ).count()

        # Obtém os vídeos do monitoramento
        videos = db.query(MonitoringVideo).filter(
            MonitoringVideo.monitoring_id == monitoring.id
        ).all()

        # Obtém os IDs das playlists do monitoramento
        playlists = [
            playlist.playlist_id 
            for playlist in db.query(MonitoringPlaylist.playlist_id).filter(
                MonitoringPlaylist.monitoring_id == monitoring.id
            ).all()
        ]

        return {
            **monitoring.__dict__,
            "channel_name": channel.channel_name,
            "channel_avatar": channel.avatar_image,
            "total_videos": total_videos,
            "processed_videos": processed_videos,
            "videos": videos,
            "playlists": playlists
        }

    def create_with_videos(
        self,
        db: Session,
        *,
        obj_in: MonitoringCreate,
        videos: List[YoutubeVideo],
        user_id: int
    ) -> YoutubeMonitoring:
        # Cria o monitoramento
        db_obj = YoutubeMonitoring(
            channel_id=obj_in.channel_id,
            name=obj_in.name,
            is_continuous=obj_in.is_continuous,
            interval_time=obj_in.interval_time,
            status=MonitoringStatus.active,
            created_by=user_id,
            next_check_at=func.now()
        )
        db.add(db_obj)
        db.flush()

        # Adiciona os vídeos ao monitoramento
        for video in videos:
            monitoring_video = MonitoringVideo(
                monitoring_id=db_obj.id,
                video_id=video.id,
                status=VideoProcessingStatus.pending,
                created_by=user_id
            )
            db.add(monitoring_video)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def _get_interval_delta(self, interval_time: int) -> timedelta:
        """
        Converte o intervalo em minutos para um objeto timedelta.
        """
        return timedelta(minutes=interval_time)

    def update(
        self,
        db: Session,
        *,
        db_obj: YoutubeMonitoring,
        obj_in: Union[MonitoringUpdate, Dict[str, Any]],
        user_id: int
    ) -> YoutubeMonitoring:
        """
        Atualiza um monitoramento existente.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Atualiza o usuário que fez a alteração
        update_data["updated_by"] = user_id
        update_data["updated_at"] = datetime.now()

        # Se o status foi alterado para ativo, atualiza o next_check_at
        if update_data.get("status") == "active":
            db_obj.next_check_at = datetime.now()

        # Se o monitoramento é contínuo, calcula o próximo check
        if update_data.get("is_continuous") and update_data.get("interval_time"):
            interval_delta = self._get_interval_delta(update_data["interval_time"])
            db_obj.next_check_at = datetime.now() + interval_delta

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def create_with_owner(
        self,
        db: Session,
        *,
        obj_in: MonitoringCreate,
        owner_id: int,
        status: MonitoringStatus = MonitoringStatus.not_configured
    ) -> YoutubeMonitoring:
        """
        Cria um novo monitoramento com o usuário dono e status inicial.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            created_by=owner_id,
            status=status
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_playlists(
        self, db: Session, *, obj_in: MonitoringCreate, user_id: int
    ) -> YoutubeMonitoring:
        """
        Cria um novo monitoramento com suas playlists.
        """
        # Cria o monitoramento
        db_obj = YoutubeMonitoring(
            channel_id=obj_in.channel_id,
            name=obj_in.name,
            is_continuous=obj_in.is_continuous,
            interval_time=obj_in.interval_time,
            created_by=user_id,
            status=MonitoringStatus.active
        )
        db.add(db_obj)
        db.flush()  # Obtém o ID do monitoramento sem commitar

        # Adiciona as playlists se fornecidas
        if obj_in.playlist_ids:
            for playlist_id in obj_in.playlist_ids:
                playlist = MonitoringPlaylist(
                    monitoring_id=db_obj.id,
                    playlist_id=playlist_id
                )
                db.add(playlist)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_playlists(
        self, db: Session, *, monitoring_id: int, playlist_ids: List[str]
    ) -> YoutubeMonitoring:
        """
        Atualiza as playlists de um monitoramento.
        """
        # Obtém o monitoramento
        monitoring = self.get(db, id=monitoring_id)
        if not monitoring:
            raise ValueError("Monitoramento não encontrado")

        # Remove todas as playlists existentes
        db.query(MonitoringPlaylist).filter(
            MonitoringPlaylist.monitoring_id == monitoring_id
        ).delete()

        # Adiciona as novas playlists
        for playlist_id in playlist_ids:
            playlist = MonitoringPlaylist(
                monitoring_id=monitoring_id,
                playlist_id=playlist_id
            )
            db.add(playlist)

        db.commit()
        db.refresh(monitoring)
        return monitoring


crud_monitoring = CRUDMonitoring() 