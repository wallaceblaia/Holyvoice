from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_monitoring import crud_monitoring
from app.crud.crud_youtube import crud_youtube
from app import models, schemas
from app.api import deps
from app.core.security import get_current_active_user

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
def create_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    monitoring_in: schemas.MonitoringCreate,
) -> Any:
    """
    Cria um novo monitoramento.
    """
    # Verifica se o usuário tem acesso ao canal
    if not crud_youtube.user_can_access_channel(
        db, user_id=current_user.id, channel_id=monitoring_in.channel_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão de acesso ao canal"
        )

    # Define o status inicial baseado na configuração
    initial_status = models.MonitoringStatus.active if (
        monitoring_in.is_continuous or (monitoring_in.videos and len(monitoring_in.videos) > 0)
    ) else models.MonitoringStatus.not_configured

    # Se tiver vídeos, cria com os vídeos
    if monitoring_in.videos:
        videos = crud_youtube.get_videos_by_ids(db, video_ids=monitoring_in.videos)
        monitoring = crud_monitoring.create_with_videos(
            db=db,
            obj_in=monitoring_in,
            videos=videos,
            user_id=current_user.id
        )
    else:
        # Cria o monitoramento sem vídeos
        monitoring = crud_monitoring.create_with_owner(
            db=db,
            obj_in=monitoring_in,
            owner_id=current_user.id,
            status=initial_status
        )

    return monitoring


@router.get("/{monitoring_id}", response_model=schemas.MonitoringWithDetails)
def get_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
    monitoring_id: int
):
    """
    Retorna os detalhes de um monitoramento específico.
    """
    monitoring = crud_monitoring.get_with_details(db, id=monitoring_id)
    if not monitoring:
        raise HTTPException(status_code=404, detail="Monitoramento não encontrado")
    
    if not crud_youtube.user_can_access_channel(
        db, user_id=current_user.id, channel_id=monitoring.channel_id
    ):
        raise HTTPException(status_code=403, detail="Sem permissão de acesso")
    
    return monitoring


@router.put("/{monitoring_id}", response_model=schemas.MonitoringWithDetails)
def update_monitoring(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
    monitoring_id: int,
    monitoring_in: schemas.MonitoringUpdate
):
    """
    Atualiza um monitoramento existente.
    """
    monitoring = crud_monitoring.get(db, id=monitoring_id)
    if not monitoring:
        raise HTTPException(status_code=404, detail="Monitoramento não encontrado")
    
    if not crud_youtube.user_can_access_channel(
        db, user_id=current_user.id, channel_id=monitoring.channel_id
    ):
        raise HTTPException(status_code=403, detail="Sem permissão de acesso")
    
    monitoring = crud_monitoring.update(
        db,
        db_obj=monitoring,
        obj_in=monitoring_in,
        user_id=current_user.id
    )
    return crud_monitoring.get_with_details(db, id=monitoring.id)


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