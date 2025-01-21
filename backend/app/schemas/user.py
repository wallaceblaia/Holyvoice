from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Propriedades compartilhadas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    name: Optional[str] = None
    avatar: Optional[str] = None


# Propriedades para criar usuário
class UserCreate(UserBase):
    email: EmailStr
    password: str
    confirm_password: str
    name: str


# Propriedades para atualizar usuário
class UserUpdate(UserBase):
    password: Optional[str] = None
    avatar: Optional[str] = None


# Propriedades compartilhadas para leitura
class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Propriedades adicionais para retornar via API
class User(UserInDBBase):
    pass


# Propriedades adicionais armazenadas no DB
class UserInDB(UserInDBBase):
    hashed_password: str 