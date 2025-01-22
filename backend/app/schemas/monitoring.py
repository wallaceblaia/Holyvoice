from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.monitoring import MonitoringInterval, MonitoringStatus, VideoProcessingStatus


# Schemas para MonitoringPlaylist
class MonitoringPlaylistBase(BaseModel):
    playlist_id: str = Field(..., description="ID da playlist no YouTube")


class MonitoringPlaylistCreate(MonitoringPlaylistBase):
    pass


class MonitoringPlaylistInDB(MonitoringPlaylistBase):
    id: int
    monitoring_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas para MonitoringVideo
class MonitoringVideoBase(BaseModel):
    video_id: int


class MonitoringVideoCreate(MonitoringVideoBase):
    pass


class MonitoringVideoUpdate(BaseModel):
    status: Optional[VideoProcessingStatus] = None
    error_message: Optional[str] = None


class MonitoringVideoInDB(MonitoringVideoBase):
    id: int
    monitoring_id: int
    status: VideoProcessingStatus
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# Schemas para Monitoring
class MonitoringBase(BaseModel):
    name: str
    channel_id: int
    is_continuous: bool = False
    interval_time: Optional[int] = None  # Intervalo em minutos
    status: str = "not_configured"


class MonitoringCreate(MonitoringBase):
    playlist_ids: Optional[List[str]] = None


class MonitoringUpdate(BaseModel):
    name: Optional[str] = None
    is_continuous: Optional[bool] = None
    interval_time: Optional[int] = None  # Intervalo em minutos
    status: Optional[str] = None
    playlist_ids: Optional[List[str]] = None


class MonitoringInDB(MonitoringBase):
    id: int
    created_by: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_check_at: Optional[datetime] = None
    next_check_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema para resposta completa com informações do canal
class MonitoringWithDetails(MonitoringInDB):
    total_videos: int
    processed_videos: int
    playlists: List[str]

    class Config:
        from_attributes = True


# Schema para listagem com informações resumidas
class MonitoringListItem(BaseModel):
    id: int
    name: str
    channel_name: str
    channel_avatar: Optional[str]
    status: MonitoringStatus
    is_continuous: bool
    interval_time: Optional[int]  # Intervalo em minutos
    created_at: datetime
    last_check_at: Optional[datetime]
    total_videos: int
    processed_videos: int

    class Config:
        from_attributes = True 