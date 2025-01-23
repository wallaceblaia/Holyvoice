from typing import Dict, Any
from sqlalchemy.orm import Session
import asyncio
import os
from fastapi import WebSocket

from app.models import (
    YoutubeMonitoring, MonitoringVideo, 
    MonitoringStatus, VideoProcessingStatus
)
from app.services.video_download.service import VideoDownloadService

class MonitoringProcessor:
    def __init__(self, db: Session):
        self.db = db
        self._active_monitorings: Dict[int, bool] = {}
        self._video_service = VideoDownloadService(db)

    def _create_project_directories(self, monitoring_id: int) -> Dict[str, str]:
        """
        Cria a estrutura de diretórios para o monitoramento.
        """
        base_path = f"downloads/{monitoring_id}"
        directories = {
            "source": f"{base_path}/source",
            "audios": f"{base_path}/audios",
            "videos": f"{base_path}/videos",
            "docs": f"{base_path}/docs",
            "legendas": f"{base_path}/legendas",
            "assets": f"{base_path}/assets",
            "imagens": f"{base_path}/imagens",
            "voices": f"{base_path}/voices",
            "lives": f"{base_path}/lives"
        }

        # Cria os diretórios
        for dir_path in directories.values():
            os.makedirs(dir_path, exist_ok=True)

        return directories

    async def start_monitoring(self, monitoring_id: int) -> None:
        """
        Inicia o processamento de um monitoramento.
        """
        # Verifica se o monitoramento existe e está no estado correto
        monitoring = self.db.query(YoutubeMonitoring).filter(
            YoutubeMonitoring.id == monitoring_id
        ).first()

        if not monitoring:
            raise ValueError("Monitoramento não encontrado")

        # Marca como ativo
        self._active_monitorings[monitoring_id] = True

        try:
            # Cria diretórios do projeto
            directories = self._create_project_directories(monitoring_id)

            # Atualiza status do monitoramento
            monitoring.status = MonitoringStatus.active
            self.db.commit()

            # Busca todos os vídeos do monitoramento
            videos = self.db.query(MonitoringVideo).filter(
                MonitoringVideo.monitoring_id == monitoring_id,
                MonitoringVideo.status.in_([
                    VideoProcessingStatus.pending,
                    VideoProcessingStatus.paused,
                    VideoProcessingStatus.error
                ])
            ).all()

            total_videos = len(videos)
            processed_videos = 0

            # Processa cada vídeo sequencialmente
            for video in videos:
                if not self._active_monitorings.get(monitoring_id):
                    video.status = VideoProcessingStatus.paused
                    self.db.commit()
                    break

                try:
                    # Atualiza status do vídeo
                    video.status = VideoProcessingStatus.downloading
                    video.project_path = f"downloads/{monitoring_id}"
                    self.db.commit()

                    # Inicia o download do vídeo
                    await self._video_service.download(
                        url=f"https://www.youtube.com/watch?v={video.video.video_id}",
                        monitoring_id=video.id
                    )

                    # Aguarda o download completar
                    while video.download_progress < 100 and self._active_monitorings.get(monitoring_id):
                        await asyncio.sleep(1)
                        self.db.refresh(video)

                    if video.download_progress >= 100:
                        video.status = VideoProcessingStatus.completed
                        processed_videos += 1
                    elif not self._active_monitorings.get(monitoring_id):
                        video.status = VideoProcessingStatus.paused
                    
                    self.db.commit()

                except Exception as e:
                    video.status = VideoProcessingStatus.error
                    video.error_message = str(e)
                    self.db.commit()

            # Atualiza status final do monitoramento
            monitoring = self.db.query(YoutubeMonitoring).get(monitoring_id)
            if monitoring:
                if processed_videos == total_videos:
                    monitoring.status = MonitoringStatus.completed
                elif not self._active_monitorings.get(monitoring_id):
                    monitoring.status = MonitoringStatus.paused
                else:
                    monitoring.status = MonitoringStatus.error
                self.db.commit()

        except Exception as e:
            # Em caso de erro, atualiza o status do monitoramento
            monitoring = self.db.query(YoutubeMonitoring).get(monitoring_id)
            if monitoring:
                monitoring.status = MonitoringStatus.error
                self.db.commit()
            raise

        finally:
            # Remove da lista de ativos
            self._active_monitorings.pop(monitoring_id, None)

    def stop_monitoring(self, monitoring_id: int) -> None:
        """
        Para o processamento de um monitoramento.
        """
        if monitoring_id in self._active_monitorings:
            self._active_monitorings[monitoring_id] = False
            
            # Atualiza status do monitoramento
            monitoring = self.db.query(YoutubeMonitoring).get(monitoring_id)
            if monitoring:
                monitoring.status = MonitoringStatus.paused
                self.db.commit()

            # Atualiza status dos vídeos em processamento
            videos = self.db.query(MonitoringVideo).filter(
                MonitoringVideo.monitoring_id == monitoring_id,
                MonitoringVideo.status == VideoProcessingStatus.downloading
            ).all()

            for video in videos:
                video.status = VideoProcessingStatus.paused
                self.db.commit() 