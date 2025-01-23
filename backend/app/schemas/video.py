from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional
from enum import Enum

class DownloadStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    completed = "completed"
    error = "error"

class ProjectDirectories(BaseModel):
    source: str
    audios: str
    videos: str
    docs: str
    legendas: str
    assets: str
    imagens: str
    voices: str
    lives: str

class VideoMetadata(BaseModel):
    title: str
    duration: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    description: Optional[str] = None

class VideoCreate(BaseModel):
    url: HttpUrl
    title: str

class VideoDownloadRequest(BaseModel):
    url: HttpUrl
    monitoring_id: int

class VideoDownloadResponse(BaseModel):
    id: int
    url: str
    title: str
    download_progress: float = 0.0
    project_path: str
    video_path: str
    source_path: Optional[str] = None
    metadata: VideoMetadata
    directories: ProjectDirectories
    download_status: DownloadStatus = DownloadStatus.pending 