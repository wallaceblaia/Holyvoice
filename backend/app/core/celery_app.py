from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.worker.monitoring"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configura tarefas periódicas
celery_app.conf.beat_schedule = {
    "check-monitoring-videos": {
        "task": "check_monitoring_videos",
        "schedule": crontab(minute="*/5"),  # A cada 5 minutos
    },
} 