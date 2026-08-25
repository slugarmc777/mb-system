"""Esquema de salida para consultar el historial de logins/logouts."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LoginHistoryOut(BaseModel):
    id: int
    user_id: Optional[int]
    username_attempted: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    login_at: datetime
    logout_at: Optional[datetime]
    success: bool
    failure_reason: Optional[str]

    class Config:
        from_attributes = True
