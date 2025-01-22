from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class YoutubeChannel(Base):
    __tablename__ = "youtube_channel"

    id = Column(Integer, primary_key=True, index=True)
    channel_url = Column(String, nullable=False)
    youtube_id = Column(String, nullable=False, index=True)  # ID do canal no YouTube
    channel_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    banner_image = Column(String, nullable=True)
    avatar_image = Column(String, nullable=True)
    subscriber_count = Column(Integer, nullable=True)
    video_count = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    api_key = Column(String, nullable=False)  # Será criptografada
    
    # Campos de auditoria
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    creator = relationship("User", foreign_keys=[created_by], backref="created_channels")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_channels")
    playlists = relationship("YoutubePlaylist", back_populates="channel", cascade="all, delete-orphan")
    videos = relationship("YoutubeVideo", back_populates="channel", cascade="all, delete-orphan")
    access_permissions = relationship("YoutubeChannelAccess", back_populates="channel", cascade="all, delete-orphan")
    monitorings = relationship("YoutubeMonitoring", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<YoutubeChannel {self.channel_name}>"


class YoutubePlaylist(Base):
    __tablename__ = "youtube_playlist"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("youtube_channel.id"), nullable=False)
    playlist_id = Column(String, nullable=False, index=True)  # ID da playlist no YouTube
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    video_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    channel = relationship("YoutubeChannel", back_populates="playlists")
    videos = relationship("YoutubeVideo", back_populates="playlist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<YoutubePlaylist {self.title}>"


class YoutubeVideo(Base):
    __tablename__ = "youtube_video"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("youtube_channel.id"), nullable=False)
    playlist_id = Column(Integer, ForeignKey("youtube_playlist.id"), nullable=True)
    video_id = Column(String, nullable=False, index=True)  # ID do vídeo no YouTube
    title = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    is_live = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    channel = relationship("YoutubeChannel", back_populates="videos")
    playlist = relationship("YoutubePlaylist", back_populates="videos")

    def __repr__(self):
        return f"<YoutubeVideo {self.title}>"


class YoutubeChannelAccess(Base):
    __tablename__ = "youtube_channel_access"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("youtube_channel.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    channel = relationship("YoutubeChannel", back_populates="access_permissions")
    user = relationship("User", foreign_keys=[user_id], backref="youtube_channel_access")
    creator = relationship("User", foreign_keys=[created_by], backref="granted_youtube_access")

    def __repr__(self):
        return f"<YoutubeChannelAccess channel={self.channel_id} user={self.user_id}>" 