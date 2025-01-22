from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import crud, models
from app.db.session import SessionLocal
from app.core.celery_app import celery_app


@celery_app.task(name="check_monitoring_videos")
def check_monitoring_videos():
    """
    Verifica os monitoramentos ativos e processa os vídeos pendentes.
    """
    db = SessionLocal()
    try:
        # Busca monitoramentos ativos que precisam ser verificados
        monitorings = db.query(models.YoutubeMonitoring).filter(
            models.YoutubeMonitoring.status == models.MonitoringStatus.ACTIVE,
            models.YoutubeMonitoring.is_continuous == True,
            models.YoutubeMonitoring.next_check_at <= datetime.utcnow()
        ).all()

        for monitoring in monitorings:
            process_monitoring.delay(monitoring.id)

            # Atualiza o próximo horário de verificação
            monitoring.last_check_at = datetime.utcnow()
            if monitoring.interval_time:
                monitoring.next_check_at = datetime.utcnow() + _get_interval_delta(
                    monitoring.interval_time
                )
            db.add(monitoring)

        db.commit()
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


def _get_interval_delta(interval: str) -> timedelta:
    """
    Converte o intervalo em um objeto timedelta.
    """
    intervals = {
        "10_minutes": timedelta(minutes=10),
        "20_minutes": timedelta(minutes=20),
        "30_minutes": timedelta(minutes=30),
        "45_minutes": timedelta(minutes=45),
        "1_hour": timedelta(hours=1),
        "2_hours": timedelta(hours=2),
        "5_hours": timedelta(hours=5),
        "12_hours": timedelta(hours=12),
        "1_day": timedelta(days=1),
        "2_days": timedelta(days=2),
        "1_week": timedelta(weeks=1),
        "1_month": timedelta(days=30),  # Aproximação
    }
    return intervals.get(interval, timedelta(hours=1)) 