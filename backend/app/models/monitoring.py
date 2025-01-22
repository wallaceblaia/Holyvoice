from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base


class MonitoringInterval(str, enum.Enum):
    MIN_10 = "10_minutes"
    MIN_20 = "20_minutes"
    MIN_30 = "30_minutes"
    MIN_45 = "45_minutes"
    HOUR_1 = "1_hour"
    HOUR_2 = "2_hours"
    HOUR_5 = "5_hours"
    HOUR_12 = "12_hours"
    DAY_1 = "1_day"
    DAY_2 = "2_days"
    WEEK_1 = "1_week"
    MONTH_1 = "1_month"


class MonitoringStatus(str, enum.Enum):
    not_configured = "not_configured"  # Monitoramento criado mas não configurado
    active = "active"                 # Monitoramento ativo
    paused = "paused"                # Monitoramento pausado
    completed = "completed"          # Monitoramento concluído
    error = "error"                  # Erro no monitoramento


class VideoProcessingStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    error = "error"
    skipped = "skipped"


class MonitoringPlaylist(Base):
    __tablename__ = "monitoring_playlist"

    id = Column(Integer, primary_key=True, index=True)
    monitoring_id = Column(Integer, ForeignKey("youtube_monitoring.id"), nullable=False)
    playlist_id = Column(String, nullable=False)  # ID da playlist no YouTube
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    monitoring = relationship("YoutubeMonitoring", back_populates="playlists")

    def __repr__(self):
        return f"<MonitoringPlaylist monitoring={self.monitoring_id} playlist={self.playlist_id}>"


class YoutubeMonitoring(Base):
    __tablename__ = "youtube_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("youtube_channel.id"), nullable=False)
    name = Column(String, nullable=False)
    is_continuous = Column(Boolean, nullable=False, default=False)
    interval_time = Column(Integer, nullable=True)  # Intervalo em minutos
    status = Column(Enum(MonitoringStatus), nullable=False, default=MonitoringStatus.not_configured)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    next_check_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    channel = relationship("YoutubeChannel", back_populates="monitorings")
    videos = relationship("MonitoringVideo", back_populates="monitoring", cascade="all, delete-orphan")
    playlists = relationship("MonitoringPlaylist", back_populates="monitoring", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<YoutubeMonitoring name={self.name} channel={self.channel_id}>"


class MonitoringVideo(Base):
    __tablename__ = "monitoring_video"

    id = Column(Integer, primary_key=True, index=True)
    monitoring_id = Column(Integer, ForeignKey("youtube_monitoring.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("youtube_video.id"), nullable=False)
    status = Column(
        Enum(VideoProcessingStatus),
        nullable=False,
        default=VideoProcessingStatus.pending
    )
    
    # Campos de auditoria
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relacionamentos
    monitoring = relationship("YoutubeMonitoring", back_populates="videos")
    video = relationship("YoutubeVideo", backref="monitoring_videos")
    creator = relationship("User", foreign_keys=[created_by], backref="created_monitoring_videos")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_monitoring_videos")

    def __repr__(self):
        return f"<MonitoringVideo monitoring={self.monitoring_id} video={self.video_id}>" 