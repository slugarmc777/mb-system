"""
Funciones criptograficas del sistema:

- Hash y verificacion de contrasenas con Argon2 (recomendado por OWASP,
  mas resistente a GPU/ASIC que bcrypt/PBKDF2).
- Creacion y decodificacion de JWT (access y refresh) firmados con HS256.
"""
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera el hash Argon2 de una contrasena en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Compara una contrasena en texto plano contra su hash almacenado."""
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str) -> str:
    """Crea un JWT de acceso de vida corta (ACCESS_TOKEN_EXPIRE_MINUTES)."""
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, jti: str, expires_at: datetime) -> str:
    """Crea un JWT de refresh; el jti debe coincidir con el registrado en DB."""
    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": expires_at,
        "jti": jti,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica y valida la firma/expiracion de cualquier JWT propio."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
