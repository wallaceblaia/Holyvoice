from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import crud, models
from app.db.session import SessionLocal
from app.core.celery_app import celery_app
from app.services.youtube_service import YouTubeService


@celery_app.task(name="check_monitoring_videos")
def check_monitoring_videos():
    """
    Verifica os vídeos dos monitoramentos ativos.
    """
    db = SessionLocal()
    try:
        # Busca monitoramentos ativos que precisam ser verificados
        monitorings = db.query(models.YoutubeMonitoring).filter(
            models.YoutubeMonitoring.status == "active",
            models.YoutubeMonitoring.next_check_at <= datetime.now(),
        ).all()

        for monitoring in monitorings:
            try:
                # Busca o canal
                channel = db.query(models.YoutubeChannel).filter(
                    models.YoutubeChannel.id == monitoring.channel_id
                ).first()

                if not channel:
                    continue

                # Busca os vídeos do canal
                youtube_service = YouTubeService(api_key=decrypted_api_key)
                videos = youtube_service.get_recent_videos(channel.channel_url)

                # Processa os vídeos
                for video in videos:
                    # Verifica se o vídeo já existe
                    db_video = db.query(models.YoutubeVideo).filter(
                        models.YoutubeVideo.video_id == video["video_id"]
                    ).first()

                    if db_video:
                        # Atualiza o vídeo
                        for key, value in video.items():
                            setattr(db_video, key, value)
                    else:
                        # Cria o vídeo
                        db_video = models.YoutubeVideo(**video, channel_id=channel.id)
                        db.add(db_video)

                    # Verifica se o vídeo já está no monitoramento
                    monitoring_video = db.query(models.MonitoringVideo).filter(
                        models.MonitoringVideo.monitoring_id == monitoring.id,
                        models.MonitoringVideo.video_id == db_video.id,
                    ).first()

                    if not monitoring_video:
                        # Adiciona o vídeo ao monitoramento
                        monitoring_video = models.MonitoringVideo(
                            monitoring_id=monitoring.id,
                            video_id=db_video.id,
                        )
                        db.add(monitoring_video)

                # Atualiza o último check
                monitoring.last_check_at = datetime.now()

                # Se for monitoramento contínuo, calcula o próximo check
                if monitoring.is_continuous and monitoring.interval_time:
                    interval_delta = _get_interval_delta(monitoring.interval_time)
                    monitoring.next_check_at = datetime.now() + interval_delta

                db.commit()

            except Exception as e:
                db.rollback()
                continue

    except Exception as e:
        db.rollback()
    finally:
        db.close()


@celery_app.task(name="process_monitoring")
def process_monitoring(monitoring_id: int):
    """
    Processa os vídeos de um monitoramento.
    """
    db = SessionLocal()
    try:
        monitoring = crud.monitoring.get(db, id=monitoring_id)
        if not monitoring:
            return

        # Busca vídeos pendentes
        videos = db.query(models.MonitoringVideo).filter(
            models.MonitoringVideo.monitoring_id == monitoring_id,
            models.MonitoringVideo.status == models.VideoProcessingStatus.PENDING
        ).all()

        for video in videos:
            process_video.delay(video.id)

    finally:
        db.close()


@celery_app.task(name="process_video")
def process_video(video_id: int):
    """
    Processa um vídeo específico.
    """
    db = SessionLocal()
    try:
        video = db.query(models.MonitoringVideo).filter(
            models.MonitoringVideo.id == video_id
        ).first()
        if not video:
            return

        video.status = models.VideoProcessingStatus.PROCESSING
        db.add(video)
        db.commit()

        try:
            # TODO: Implementar o processamento do vídeo
            # 1. Download do vídeo
            # 2. Extração do áudio
            # 3. Tradução
            # 4. Dublagem
            # 5. Upload do resultado

            video.status = models.VideoProcessingStatus.COMPLETED
            video.processed_at = datetime.utcnow()
        except Exception as e:
            video.status = models.VideoProcessingStatus.ERROR
            video.error_message = str(e)

        db.add(video)
        db.commit()

    finally:
        db.close()


def _get_interval_delta(interval_time: int) -> timedelta:
    """
    Converte o intervalo em minutos para um objeto timedelta.
    """
    return timedelta(minutes=interval_time) 