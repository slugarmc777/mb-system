"""Esquemas Pydantic para el flujo de autenticacion (tokens, refresh, logout)."""
from pydantic import BaseModel


class TokenPair(BaseModel):
    """Respuesta de /auth/login: access token de vida corta + refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    """Respuesta de /auth/refresh: solo un access token nuevo."""
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
