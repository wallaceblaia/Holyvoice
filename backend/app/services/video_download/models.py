from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class VideoDownloadRequest(BaseModel):
    url: str
    monitoring_id: int

class DownloadProgress(BaseModel):
    monitoring_id: int
    step: str = "Downloading"
    progress: float
    speed: Optional[str]
    eta: Optional[str]
    downloaded_bytes: Optional[int]
    total_bytes: Optional[int]

class VideoMetadata(BaseModel):
    title: str
    description: Optional[str]
    view_count: Optional[int]
    duration: Optional[int]
    video_quality: Optional[str]
    channel_title: Optional[str]
    tags: Optional[List[str]]
    category: Optional[str]
    original_language: Optional[str]
    like_count: Optional[int]
    comment_count: Optional[int]

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

class DownloadStatus(BaseModel):
    step: str
    progress: float
    started_at: datetime
    completed_at: Optional[datetime] = None

class VideoDownloadResponse(BaseModel):
    project_path: str
    video_path: str
    metadata: VideoMetadata
    directories: ProjectDirectories
    download_status: DownloadStatus 