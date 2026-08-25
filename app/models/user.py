"""
Modelo de usuario.

Guarda credenciales (hash de contrasena, nunca en texto plano), el rol
(admin/usuario) y los contadores necesarios para el bloqueo de cuenta tras
intentos fallidos de login.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    usuario = "usuario"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.usuario, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
