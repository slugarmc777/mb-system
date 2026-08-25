"""
Configuracion centralizada de la aplicacion.

Lee variables de entorno desde el archivo .env (ver .env.example) usando
pydantic-settings. Todo el resto del codigo importa `settings` desde aqui
en vez de leer os.environ directamente.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 dia

    DATABASE_URL: str = "sqlite:///./mb_system.db"

    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
