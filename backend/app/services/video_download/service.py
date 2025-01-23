import os
import yt_dlp
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
import asyncio
from fastapi import WebSocket

from app.core.config import settings
from app.models import MonitoringVideo, YoutubeVideo, VideoProcessingStatus
from app.schemas.video import (
    VideoDownloadResponse, VideoMetadata, 
    ProjectDirectories, DownloadStatus
)
from .websocket import manager

class VideoDownloadService:
    def __init__(self, db: Session):
        self.db = db
        self._progress_subscribers: Dict[int, WebSocket] = {}
        self._loop = asyncio.get_event_loop()

    async def download(self, url: str, monitoring_id: int) -> VideoDownloadResponse:
        """
        Inicia o download de um vídeo do YouTube.
        """
        # Busca o vídeo no banco
        video = self.db.query(MonitoringVideo).filter(
            MonitoringVideo.id == monitoring_id
        ).first()
        
        if not video:
            raise ValueError("Vídeo não encontrado")

        # Cria a estrutura de diretórios
        project_path = self._create_project_structure(monitoring_id)
        video_path = os.path.join(project_path, 'source', 'video.mp4')

        # Configura o yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(project_path, 'source', '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: self._progress_hook(monitoring_id, d)],
        }

        # Inicia o download em background
        asyncio.create_task(self._download_video(str(url), video, ydl_opts))

        # Atualiza o status do vídeo
        video.download_started_at = datetime.utcnow()
        video.download_progress = 0.0
        video.status = VideoProcessingStatus.downloading
        self.db.commit()

        # Cria o objeto de diretórios
        directories = ProjectDirectories(
            source=os.path.join(project_path, 'source'),
            audios=os.path.join(project_path, 'audios'),
            videos=os.path.join(project_path, 'videos'),
            docs=os.path.join(project_path, 'docs'),
            legendas=os.path.join(project_path, 'legendas'),
            assets=os.path.join(project_path, 'assets'),
            imagens=os.path.join(project_path, 'imagens'),
            voices=os.path.join(project_path, 'voices'),
            lives=os.path.join(project_path, 'lives')
        )

        # Cria o objeto de metadados
        metadata = VideoMetadata(
            title=video.video.title,
            duration=None,
            view_count=None,
            like_count=None,
            comment_count=None,
            description=None
        )

        return VideoDownloadResponse(
            id=video.id,
            url=str(url),
            title=video.video.title,
            download_progress=0.0,
            project_path=project_path,
            video_path=video_path,
            source_path=None,
            metadata=metadata,
            directories=directories,
            download_status=DownloadStatus(
                step=video.status,
                progress=video.download_progress or 0,
                started_at=video.download_started_at,
                completed_at=video.download_completed_at
            )
        )

    def _progress_hook(self, monitoring_id: int, d: dict) -> None:
        """
        Processa o progresso do download.
        """
        video = self.db.query(MonitoringVideo).get(monitoring_id)
        if not video:
            return

        try:
            if d['status'] == 'downloading':
                # Calcula o progresso
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    progress = 0

                # Atualiza o progresso no banco
                video.download_progress = progress
                self.db.commit()

                # Cria mensagem de status
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                status_message = f"Baixando - {d.get('_percent_str', '0%')} a {speed/1024/1024:.1f}MB/s - ETA: {eta}s"

                # Notifica progresso via WebSocket
                asyncio.create_task(self._notify_progress(monitoring_id, {
                    'progress': progress,
                    'status': 'downloading',
                    'title': video.video.title,
                    'message': status_message,
                    'speed': speed,
                    'eta': eta
                }))

        except Exception as e:
            # Log do erro mas continua o processo
            print(f"Erro ao processar progresso: {str(e)}")

    async def _download_video(self, url: str, video: MonitoringVideo, opts: dict):
        """
        Realiza o download do vídeo em background.
        """
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Atualiza informações do vídeo
                youtube_video = video.video
                youtube_video.title = info.get('title')
                video.source_path = os.path.join(
                    video.project_path, 
                    'source', 
                    ydl.prepare_filename(info)
                )
                video.download_completed_at = datetime.utcnow()
                video.status = VideoProcessingStatus.completed
                self.db.commit()

                # Notifica conclusão
                await self._notify_progress(video.id, {
                    'progress': 100,
                    'status': 'completed',
                    'title': info.get('title', ''),
                    'message': 'Download concluído'
                })

        except Exception as e:
            video.status = VideoProcessingStatus.error
            video.error_message = str(e)
            self.db.commit()
            
            # Notifica erro
            await self._notify_progress(video.id, {
                'progress': video.download_progress or 0,
                'status': 'error',
                'message': str(e)
            })
            raise

    async def subscribe_to_progress(self, websocket: WebSocket, monitoring_id: int):
        """
        Registra um WebSocket para receber atualizações de progresso.
        """
        await websocket.accept()
        self._progress_subscribers[monitoring_id] = websocket

        try:
            while True:
                await websocket.receive_text()
        except:
            self._progress_subscribers.pop(monitoring_id, None)

    async def _notify_progress(self, monitoring_id: int, data: Dict[str, Any]):
        """
        Notifica o progresso via WebSocket.
        """
        if monitoring_id in self._progress_subscribers:
            try:
                await self._progress_subscribers[monitoring_id].send_json(data)
            except:
                self._progress_subscribers.pop(monitoring_id, None)

    def _create_project_structure(self, monitoring_id: int) -> str:
        """Cria a estrutura de diretórios do projeto"""
        base_path = os.path.join('downloads', str(monitoring_id))
        directories = [
            'source', 'audios', 'videos', 'docs', 'legendas',
            'assets', 'imagens', 'voices', 'lives'
        ]
        
        for dir_name in directories:
            dir_path = os.path.join(base_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            
        return base_path

    def _get_ytdl_options(self, project_path: str, monitoring_id: int) -> Dict[str, Any]:
        """Configura as opções do yt-dlp"""
        return {
            'format': settings.YTDLP_FORMAT,
            'outtmpl': os.path.join(project_path, 'source', 'mainvideo.mp4'),
            'progress_hooks': [lambda d: self._progress_hook(monitoring_id, d)],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }

    def _get_monitoring_video(self, monitoring_id: int) -> MonitoringVideo:
        """Obtém o registro do vídeo no monitoramento"""
        return self.db.query(MonitoringVideo).filter(
            MonitoringVideo.id == monitoring_id
        ).first()

    def _update_video_metadata(self, monitoring_video: MonitoringVideo, info: Dict[str, Any]):
        """Atualiza os metadados do vídeo no banco de dados"""
        youtube_video = monitoring_video.video
        
        # Atualizar informações do vídeo
        youtube_video.title = info.get('title')
        youtube_video.description = info.get('description')
        youtube_video.view_count = info.get('view_count')
        youtube_video.duration = info.get('duration')
        youtube_video.video_quality = info.get('format_note')
        youtube_video.tags = info.get('tags', [])
        youtube_video.category = info.get('categories', [None])[0]
        youtube_video.original_language = info.get('language')
        youtube_video.like_count = info.get('like_count')
        youtube_video.comment_count = info.get('comment_count')
        
        self.db.commit()

    def _create_response(self, project_path: str, monitoring_video: MonitoringVideo) -> VideoDownloadResponse:
        """Cria o objeto de resposta"""
        video = monitoring_video.video
        
        return VideoDownloadResponse(
            project_path=project_path,
            video_path=os.path.join(project_path, 'source', 'mainvideo.mp4'),
            metadata=VideoMetadata(
                title=video.title,
                description=video.description,
                view_count=video.view_count,
                duration=video.duration,
                video_quality=video.video_quality,
                channel_title=video.channel.channel_name,
                tags=video.tags,
                category=video.category,
                original_language=video.original_language,
                like_count=video.like_count,
                comment_count=video.comment_count
            ),
            directories=ProjectDirectories(
                source=os.path.join(project_path, 'source'),
                audios=os.path.join(project_path, 'audios'),
                videos=os.path.join(project_path, 'videos'),
                docs=os.path.join(project_path, 'docs'),
                legendas=os.path.join(project_path, 'legendas'),
                assets=os.path.join(project_path, 'assets'),
                imagens=os.path.join(project_path, 'imagens'),
                voices=os.path.join(project_path, 'voices'),
                lives=os.path.join(project_path, 'lives')
            ),
            download_status=DownloadStatus(
                step=monitoring_video.status,
                progress=monitoring_video.download_progress or 0,
                started_at=monitoring_video.download_started_at,
                completed_at=monitoring_video.download_completed_at
            )
        )

    def _handle_error(self, monitoring_video: MonitoringVideo, error_message: str):
        """Trata erros durante o download"""
        monitoring_video.status = "Error"
        monitoring_video.error_message = error_message
        monitoring_video.download_completed_at = datetime.utcnow()
        self.db.commit() 