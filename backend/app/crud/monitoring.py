from typing import List, Optional, Union, Dict, Any
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, select, join, case

from app.crud.base import CRUDBase
from app.models.monitoring import YoutubeMonitoring, MonitoringVideo, MonitoringStatus
from app.models.youtube import YoutubeChannel
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
    ) -> List[Dict[str, Any]]:
        query = db.query(
            YoutubeMonitoring,
            YoutubeChannel.name.label("channel_name"),
            YoutubeChannel.avatar_image.label("channel_avatar"),
            func.count(MonitoringVideo.id).label("total_videos"),
            func.count(case([(MonitoringVideo.status == "completed", 1)])).label("processed_videos")
        ).join(
            YoutubeChannel,
            YoutubeMonitoring.channel_id == YoutubeChannel.id
        ).outerjoin(
            MonitoringVideo,
            YoutubeMonitoring.id == MonitoringVideo.monitoring_id
        ).filter(
            YoutubeMonitoring.created_by == user_id
        )

        if status:
            query = query.filter(YoutubeMonitoring.status == status)

        results = query.group_by(
            YoutubeMonitoring.id,
            YoutubeChannel.name,
            YoutubeChannel.avatar_image
        ).order_by(
            YoutubeMonitoring.created_at.desc()
        ).offset(skip).limit(limit).all()

        return [
            {
                **jsonable_encoder(result[0]),
                "channel_name": result[1],
                "channel_avatar": result[2],
                "total_videos": result[3],
                "processed_videos": result[4]
            }
            for result in results
        ]

    def create_with_videos(
        self,
        db: Session,
        *,
        obj_in: MonitoringCreate,
        videos: List[Any],
        user_id: int
    ) -> YoutubeMonitoring:
        obj_in_data = jsonable_encoder(obj_in, exclude={"videos"})
        db_obj = self.model(
            **obj_in_data,
            created_by=user_id,
            status=MonitoringStatus.ACTIVE
        )
        db.add(db_obj)
        db.flush()  # Obtém o ID do monitoramento

        # Adiciona os vídeos ao monitoramento
        for video in videos:
            monitoring_video = MonitoringVideo(
                monitoring_id=db_obj.id,
                video_id=video.id,
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
        obj_in: Union[MonitoringUpdate, Dict[str, Any]],
        user_id: int
    ) -> YoutubeMonitoring:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        update_data["updated_by"] = user_id
        update_data["updated_at"] = func.now()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_with_details(
        self,
        db: Session,
        *,
        id: int
    ) -> Optional[Dict[str, Any]]:
        monitoring = db.query(
            self.model,
            YoutubeChannel.name.label("channel_name"),
            YoutubeChannel.avatar_image.label("channel_avatar"),
            func.count(MonitoringVideo.id).label("total_videos"),
            func.count(case([(MonitoringVideo.status == "completed", 1)])).label("processed_videos")
        ).join(
            YoutubeChannel,
            self.model.channel_id == YoutubeChannel.id
        ).outerjoin(
            MonitoringVideo,
            self.model.id == MonitoringVideo.monitoring_id
        ).filter(
            self.model.id == id
        ).group_by(
            self.model.id,
            YoutubeChannel.name,
            YoutubeChannel.avatar_image
        ).first()

        if not monitoring:
            return None

        result = {
            **jsonable_encoder(monitoring[0]),
            "channel_name": monitoring[1],
            "channel_avatar": monitoring[2],
            "total_videos": monitoring[3],
            "processed_videos": monitoring[4],
            "videos": self.get_monitoring_videos(db, monitoring_id=id)
        }
        return result

    def get_monitoring_videos(
        self,
        db: Session,
        *,
        monitoring_id: int
    ) -> List[Dict[str, Any]]:
        return db.query(MonitoringVideo).filter(
            MonitoringVideo.monitoring_id == monitoring_id
        ).all()

    def _get_interval_delta(self, interval: str) -> timedelta:
        """Converte o intervalo em um objeto timedelta."""
        intervals = {
            "10_minutes": timedelta(minutes=10),
            "20_minutes": timedelta(minutes=20),
            "30_minutes": timedelta(minutes=30),
            "45_minutes": timedelta(minutes=45),
            "1_hour": timedelta(hours=1),
            "2_hours": timedelta(hours=2),
            "5_hours": timedelta(hours=5),
            "12_hours": timedelta(hours=12),
            "1_day": timedelta(days=1),
            "2_days": timedelta(days=2),
            "1_week": timedelta(weeks=1),
            "1_month": timedelta(days=30),  # Aproximação
        }
        return intervals.get(interval, timedelta(hours=1))


monitoring = CRUDMonitoring() 