from typing import Any
from fastapi import APIRouter, Depends, WebSocket, HTTPException, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app import deps
from app.models import (
    User, MonitoringVideo, YoutubeVideo, VideoProcessingStatus,
    YoutubeMonitoring, MonitoringStatus, YoutubeChannel
)
from app.services.video_download.service import VideoDownloadService
from app.schemas.video import VideoDownloadRequest, VideoDownloadResponse, VideoCreate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/videos", response_model=VideoDownloadResponse)
async def create_video(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    video_data: VideoCreate,
) -> Any:
    """
    Cria um novo registro de vídeo.
    """
    try:
        # Primeiro verifica se já existe um canal, senão cria
        channel = db.query(YoutubeChannel).first()
        if not channel:
            channel = YoutubeChannel(
                channel_url="https://www.youtube.com/",
                youtube_id="default",
                channel_name="Default Channel",
                api_key="default",
                created_by=current_user.id
            )
            db.add(channel)
            db.commit()
            db.refresh(channel)

        # Verifica se já existe um monitoramento, senão cria
        monitoring = db.query(YoutubeMonitoring).first()
        if not monitoring:
            monitoring = YoutubeMonitoring(
                channel_id=channel.id,
                name="Download Manual",
                is_continuous=False,
                status=MonitoringStatus.active,
                created_by=current_user.id
            )
            db.add(monitoring)
            db.commit()
            db.refresh(monitoring)

        # Cria o YoutubeVideo
        youtube_video = YoutubeVideo(
            video_id=str(video_data.url).split("v=")[1].split("&")[0],  # Extrai o ID do vídeo da URL
            title=video_data.title,
            channel_id=channel.id,
            published_at=datetime.utcnow()
        )
        db.add(youtube_video)
        db.commit()
        db.refresh(youtube_video)

        # Cria o MonitoringVideo
        monitoring_video = MonitoringVideo(
            monitoring_id=monitoring.id,
            video_id=youtube_video.id,
            status=VideoProcessingStatus.pending,
            created_by=current_user.id
        )
        db.add(monitoring_video)
        db.commit()
        db.refresh(monitoring_video)

        return VideoDownloadResponse(
            id=monitoring_video.id,
            url=str(video_data.url),
            title=youtube_video.title,
            download_progress=0.0,
            project_path=None,
            source_path=None
        )
    except Exception as e:
        logger.error(f"Erro ao criar vídeo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/download", response_model=VideoDownloadResponse)
async def download_video(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    video_data: VideoDownloadRequest,
) -> Any:
    """
    Inicia o download de um vídeo.
    """
    try:
        # Verifica se o vídeo existe
        video = db.query(MonitoringVideo).filter(
            MonitoringVideo.id == video_data.monitoring_id
        ).first()
        
        if not video:
            logger.error(f"Vídeo com ID {video_data.monitoring_id} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vídeo com ID {video_data.monitoring_id} não encontrado"
            )

        logger.info(f"Iniciando download do vídeo: {video_data.url} para monitoring_id: {video_data.monitoring_id}")
        video_service = VideoDownloadService(db)
        result = await video_service.download(video_data.url, video_data.monitoring_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao fazer download do vídeo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.websocket("/ws/{monitoring_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    monitoring_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    WebSocket para atualizações em tempo real do progresso do download.
    """
    await websocket.accept()
    try:
        video_service = VideoDownloadService(db)
        await video_service.subscribe_to_progress(websocket, monitoring_id)
    except Exception as e:
        logger.error(f"Erro na conexão WebSocket: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 