from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.monitoring import (
    YoutubeMonitoring,
    MonitoringVideo,
    MonitoringStatus,
    VideoProcessingStatus
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

    def get_with_details(
        self,
        db: Session,
        *,
        id: int
    ) -> Optional[YoutubeMonitoring]:
        result = (
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
            .filter(YoutubeMonitoring.id == id)
            .group_by(YoutubeMonitoring.id, YoutubeChannel.channel_name, YoutubeChannel.avatar_image)
            .first()
        )

        if not result:
            return None

        monitoring = result[0]
        monitoring.channel_name = result[1]
        monitoring.channel_avatar = result[2]
        monitoring.total_videos = result[3]
        monitoring.processed_videos = result[4]
        
        # Carrega os vídeos relacionados
        monitoring.videos = (
            db.query(MonitoringVideo)
            .filter(MonitoringVideo.monitoring_id == id)
            .all()
        )

        return monitoring

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

    def update(
        self,
        db: Session,
        *,
        db_obj: YoutubeMonitoring,
        obj_in: MonitoringUpdate,
        user_id: int
    ) -> YoutubeMonitoring:
        update_data = obj_in.dict(exclude_unset=True)
        
        # Se o status mudou para active, atualiza next_check
        if update_data.get("status") == MonitoringStatus.ACTIVE:
            update_data["next_check"] = func.now()
        
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


crud_monitoring = CRUDMonitoring() 