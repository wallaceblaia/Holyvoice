from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import status
from datetime import datetime

from app.crud.crud_monitoring import crud_monitoring
from app.crud.crud_youtube import crud_youtube
from app import models, schemas
from app.api import deps
from app.core.security import get_current_active_user
from app.services.youtube import YouTubeService
from app.services.monitoring_processor import MonitoringProcessor

router = APIRouter()


@router.get("/", response_model=List[schemas.MonitoringListItem])
def list_monitorings(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.MonitoringStatus] = None
):
    """
    Retorna a lista de monitoramentos com informações resumidas.
    """
    return crud_monitoring.get_multi_with_details(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )


@router.post("/", response_model=schemas.MonitoringInDB)
async def create_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    monitoring_in: schemas.MonitoringCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cria um novo monitoramento.
    """
    # Verifica se o canal existe e se o usuário tem acesso
    channel = crud_youtube.get_channel(db, id=monitoring_in.channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canal não encontrado",
        )

    if not crud_youtube.user_can_access_channel(db, user_id=current_user.id, channel_id=channel.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este canal",
        )

    # Se for monitoramento contínuo, verifica se foi fornecido um intervalo
    if monitoring_in.is_continuous and not monitoring_in.interval_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Para monitoramento contínuo é necessário especificar o intervalo",
        )

    # Se foram fornecidas playlists, verifica se elas existem no canal
    if monitoring_in.playlist_ids:
        youtube_service = YouTubeService()
        playlists = await youtube_service.get_playlists(channel.channel_url)
        valid_playlist_ids = [p["playlist_id"] for p in playlists]
        
        for playlist_id in monitoring_in.playlist_ids:
            if playlist_id not in valid_playlist_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Playlist {playlist_id} não encontrada no canal",
                )

    # Cria o monitoramento com as playlists
    monitoring = crud_monitoring.create_with_playlists(
        db=db,
        obj_in=monitoring_in,
        user_id=current_user.id
    )

    return monitoring


@router.get("/{monitoring_id}", response_model=schemas.MonitoringWithDetails)
def get_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    monitoring_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retorna os detalhes de um monitoramento.
    """
    monitoring = crud_monitoring.get_with_details(db, id=monitoring_id)
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoramento não encontrado",
        )

    # Verifica se o usuário tem acesso ao canal
    if not crud_youtube.user_can_access_channel(db, user_id=current_user.id, channel_id=monitoring["channel_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este canal",
        )

    return monitoring


def _convert_interval_to_minutes(interval: str) -> int:
    """Converte o intervalo para minutos."""
    intervals = {
        "10_minutes": 10,
        "20_minutes": 20,
        "30_minutes": 30,
        "45_minutes": 45,
        "1_hour": 60,
        "2_hours": 120,
        "5_hours": 300,
        "12_hours": 720,
        "1_day": 1440,
        "2_days": 2880,
        "1_week": 10080,
        "1_month": 43200  # Aproximação de 30 dias
    }
    return intervals.get(interval, 60)  # Default para 1 hora


@router.put("/{monitoring_id}", response_model=schemas.MonitoringInDB)
async def update_monitoring(
    monitoring_id: int,
    monitoring_in: schemas.MonitoringUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Atualiza um monitoramento existente.
    """
    monitoring = crud_monitoring.get(db, id=monitoring_id)
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoramento não encontrado",
        )

    # Verifica se o usuário tem acesso ao canal
    channel = crud_youtube.get_channel(db, id=monitoring.channel_id)
    if not crud_youtube.user_can_access_channel(db, channel.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este canal",
        )

    # Se o monitoramento é contínuo, precisa ter um intervalo
    if monitoring_in.is_continuous and not monitoring_in.interval_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Para monitoramento contínuo é necessário especificar um intervalo",
        )

    # Se tem playlists, verifica se existem no canal
    if monitoring_in.playlist_ids:
        youtube_service = YouTubeService()
        try:
            playlists = await youtube_service.get_playlists(channel.channel_url)
            playlist_ids = [p["playlist_id"] for p in playlists]
            for playlist_id in monitoring_in.playlist_ids:
                if playlist_id not in playlist_ids:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Playlist {playlist_id} não encontrada no canal",
                    )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro ao validar playlists: {str(e)}",
            )

    # Atualiza o monitoramento
    monitoring = crud_monitoring.update(
        db,
        db_obj=monitoring,
        obj_in=monitoring_in,
        user_id=current_user.id,
    )

    # Se tem playlists, atualiza
    if monitoring_in.playlist_ids is not None:
        crud_monitoring.update_playlists(
            db,
            monitoring_id=monitoring.id,
            playlist_ids=monitoring_in.playlist_ids,
        )

    return monitoring


@router.delete("/{monitoring_id}")
def delete_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
    monitoring_id: int
):
    """
    Remove um monitoramento.
    """
    monitoring = crud_monitoring.get(db, id=monitoring_id)
    if not monitoring:
        raise HTTPException(status_code=404, detail="Monitoramento não encontrado")
    
    if not crud_youtube.user_can_access_channel(
        db, user_id=current_user.id, channel_id=monitoring.channel_id
    ):
        raise HTTPException(status_code=403, detail="Sem permissão de acesso")
    
    crud_monitoring.remove(db, id=monitoring_id)
    return {"message": "Monitoramento removido com sucesso"}


@router.post("/{monitoring_id}/start", response_model=Any)
async def start_monitoring(
    monitoring_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Inicia o processamento de um monitoramento.
    """
    try:
        processor = MonitoringProcessor(db)
        # Inicia o processamento em background
        background_tasks.add_task(processor.start_monitoring, monitoring_id)
        return {"message": "Processamento iniciado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{monitoring_id}/stop", response_model=Any)
async def stop_monitoring(
    monitoring_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Para o processamento de um monitoramento.
    """
    try:
        processor = MonitoringProcessor(db)
        processor.stop_monitoring(monitoring_id)
        return {"message": "Processamento interrompido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 