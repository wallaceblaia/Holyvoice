from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# Certifique-se de importar todos os modelos aqui para que o Alembic possa detectá-los
from app.db.base_class import Base
from app.db.session import engine


def init_db(db: Session) -> None:
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    # Criar usuário admin se não existir
    user = crud.user.get_by_email(db, email="admin@holyvoice.com")
    if not user:
        user_in = schemas.UserCreate(
            email="admin@holyvoice.com",
            password="admin123",
            confirm_password="admin123",
            name="Admin",
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in) 