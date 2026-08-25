"""
Modelo de historial de sesiones.

Cada intento de login (exitoso o fallido) genera una fila. Cuando el login
es exitoso se guarda tambien el `session_jti` (el jti del refresh token),
lo que permite que /auth/logout encuentre esta misma fila y complete
`logout_at`.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username_attempted = Column(String(50), nullable=True)
    session_jti = Column(String(36), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    login_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_at = Column(DateTime, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(120), nullable=True)

    user = relationship("User", back_populates="login_history")
