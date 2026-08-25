"""
Modelo de refresh token.

Un JWT firmado no se puede "borrar" del lado del servidor: por eso cada
refresh token emitido se guarda aqui (identificado por su `jti`) y se marca
`revoked=True` cuando el usuario hace logout. El endpoint /auth/refresh
valida este registro antes de emitir un access token nuevo.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
