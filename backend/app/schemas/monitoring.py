from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.monitoring import MonitoringInterval, MonitoringStatus, VideoProcessingStatus


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


# Schemas para YoutubeMonitoring
class MonitoringBase(BaseModel):
    name: str = Field(..., description="Nome do monitoramento para identificação")
    channel_id: int = Field(..., description="ID do canal do YouTube a ser monitorado")
    is_continuous: bool = Field(
        default=False,
        description="Se o monitoramento deve ser contínuo"
    )
    interval_time: Optional[MonitoringInterval] = Field(
        None,
        description="Intervalo de tempo para monitoramento contínuo"
    )


class MonitoringCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Nome do monitoramento")
    channel_id: int = Field(..., description="ID do canal a ser monitorado")
    is_continuous: bool = Field(False, description="Se o monitoramento é contínuo")
    interval_time: Optional[MonitoringInterval] = Field(None, description="Intervalo de verificação para monitoramento contínuo")
    videos: List[int] = Field(default_factory=list, description="Lista de IDs dos vídeos a monitorar")


class MonitoringUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    is_continuous: Optional[bool] = None
    interval_time: Optional[MonitoringInterval] = None
    status: Optional[MonitoringStatus] = None
    videos: Optional[List[int]] = Field(None, description="Lista de IDs dos vídeos a monitorar")


class MonitoringInDB(MonitoringBase):
    id: int
    status: MonitoringStatus
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_check_at: Optional[datetime]
    next_check_at: Optional[datetime]
    channel_name: str = ""  # Nome do canal
    channel_avatar: Optional[str] = None  # Avatar do canal
    total_videos: int = 0  # Total de vídeos monitorados
    processed_videos: int = 0  # Total de vídeos processados

    class Config:
        from_attributes = True


# Schema para resposta completa com informações do canal
class MonitoringWithDetails(MonitoringInDB):
    channel_name: str
    channel_avatar: Optional[str]
    total_videos: int
    processed_videos: int
    videos: List[MonitoringVideoInDB]

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
    interval_time: Optional[MonitoringInterval]
    created_at: datetime
    last_check_at: Optional[datetime]
    total_videos: int
    processed_videos: int

    class Config:
        from_attributes = True 