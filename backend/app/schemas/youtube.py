from datetime import datetime
from typing import List, Optional, ForwardRef
from pydantic import BaseModel, HttpUrl, EmailStr, Field, validator
import re


class YoutubeVideo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: datetime
    is_live: bool = False

    class Config:
        from_attributes = True


class YoutubePlaylistBase(BaseModel):
    playlist_id: str = Field(..., description="ID da playlist no YouTube")
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None


class YoutubePlaylistCreate(YoutubePlaylistBase):
    channel_id: int


class YoutubePlaylistUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    video_count: Optional[int] = Field(None, ge=0)


class YoutubePlaylist(YoutubePlaylistBase):
    id: int
    channel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class YoutubeChannelAccessBase(BaseModel):
    channel_id: int
    user_id: int
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False


class YoutubeChannelAccessCreate(YoutubeChannelAccessBase):
    created_by: int


class YoutubeChannelAccess(YoutubeChannelAccessBase):
    id: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True


class YoutubeChannelBase(BaseModel):
    channel_url: str = Field(..., description="URL do canal do YouTube")

    @validator('channel_url')
    def validate_channel_url(cls, v):
        # Validar formato da URL do canal do YouTube
        pattern = r'^https?:\/\/(www\.)?youtube\.com\/(channel\/UC[\w-]{21}[AQgw]|c\/[\w-]+|@[\w-]+)$'
        if not re.match(pattern, v):
            raise ValueError('URL do canal inválida. Use o formato correto do YouTube')
        return v


class YoutubeChannelCreate(YoutubeChannelBase):
    api_key: str = Field(..., min_length=30, description="API key do YouTube")

    @validator('api_key')
    def validate_api_key(cls, v):
        # Validar formato da API key do YouTube
        pattern = r'^[\w-]{39}$'
        if not re.match(pattern, v):
            raise ValueError('API key inválida. Verifique suas credenciais do YouTube')
        return v


class YoutubeChannelCreateDB(BaseModel):
    """Schema para criar canal no banco de dados (aceita API key criptografada)"""
    channel_url: str
    youtube_id: str
    channel_name: str
    api_key: str
    description: Optional[str] = None
    avatar_image: Optional[str] = None
    banner_image: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    created_by: int


class YoutubeChannelUpdate(BaseModel):
    channel_name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = Field(None, min_length=30)


class YoutubeVideoCreate(YoutubeVideo):
    channel_id: int
    playlist_id: Optional[int] = None


class YoutubeVideoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_live: Optional[bool] = None


class YoutubeChannel(YoutubeChannelBase):
    id: int
    youtube_id: str
    channel_name: str
    description: Optional[str] = None
    avatar_image: Optional[str] = None
    banner_image: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    playlists: List[YoutubePlaylist] = []
    videos: List[YoutubeVideo] = []
    access_permissions: List[YoutubeChannelAccess] = []

    class Config:
        from_attributes = True


class YoutubeChannelWithVideos(YoutubeChannel):
    recent_videos: List[YoutubeVideo]

    class Config:
        from_attributes = True 