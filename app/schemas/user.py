"""Esquemas Pydantic relacionados con el usuario (entrada/salida de la API)."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import RoleEnum


class UserCreate(BaseModel):
    """Datos requeridos para /auth/register."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    """Representacion publica de un usuario (nunca incluye el password)."""
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """Campos que el admin puede modificar de cualquier usuario."""
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    new_password: Optional[str] = Field(default=None, min_length=8, max_length=128)
