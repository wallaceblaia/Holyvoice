from typing import Any

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.crud.crud_user import crud_user
from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retorna informações do usuário atual.
    """
    return current_user

@router.patch("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    avatar: str = Body(None),
) -> Any:
    """
    Atualiza informações do usuário atual.
    """
    user_in = schemas.UserUpdate(avatar=avatar)
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user 