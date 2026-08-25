"""
Router de autenticacion: register, login, refresh y logout.

Estos son los endpoints que el frontend debe consumir para todo el ciclo
de sesion. Quedan expuestos en Swagger UI (/docs) automaticamente por ser
parte de la app de FastAPI; no hace falta configuracion adicional.
"""
import uuid
from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, RoleEnum
from app.models.token import RefreshToken
from app.models.login_history import LoginHistory
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import TokenPair, AccessToken, RefreshRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


def get_client_info(request: Request):
    """Extrae IP y user-agent del request para el log de sesiones."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return ip, ua


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint publico: crea un usuario nuevo con rol 'usuario' por defecto."""
    exists = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Usuario o email ya registrado")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=RoleEnum.usuario,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login con usuario/contrasena (formulario OAuth2, por eso en Swagger
    aparecen los campos 'username' y 'password', no JSON).

    - Registra cada intento (exitoso o fallido) en login_history.
    - Bloquea la cuenta tras MAX_LOGIN_ATTEMPTS fallos consecutivos.
    - Devuelve access_token (corto) + refresh_token (mas largo).
    """
    ip, ua = get_client_info(request)
    user = db.query(User).filter(User.username == form_data.username).first()
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contrasena incorrectos",
    )

    def log_attempt(success: bool, reason: str | None = None, uid=None, jti=None):
        db.add(LoginHistory(
            user_id=uid,
            username_attempted=form_data.username,
            session_jti=jti,
            ip_address=ip,
            user_agent=ua,
            success=success,
            failure_reason=reason,
        ))
        db.commit()

    if user is None:
        log_attempt(False, "usuario_no_existe")
        raise generic_error

    if user.locked_until and user.locked_until > datetime.utcnow():
        log_attempt(False, "cuenta_bloqueada", user.id)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta bloqueada hasta {user.locked_until.isoformat()} por multiples intentos fallidos",
        )

    if not user.is_active:
        log_attempt(False, "cuenta_inactiva", user.id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")

    if not verify_password(form_data.password, user.hashed_password):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_MINUTES)
            user.failed_attempts = 0
        db.commit()
        log_attempt(False, "password_incorrecta", user.id)
        raise generic_error

    user.failed_attempts = 0
    user.locked_until = None
    db.commit()

    access_token = create_access_token(subject=user.username, role=user.role.value)
    jti = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(subject=user.username, jti=jti, expires_at=expires_at)

    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
    log_attempt(True, None, user.id, jti)

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessToken)
def refresh_access_token(data: RefreshRequest, db: Session = Depends(get_db)):
    """Intercambia un refresh token valido (no revocado, no expirado) por un access token nuevo."""
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido o expirado")
    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        raise invalid

    if payload.get("type") != "refresh":
        raise invalid

    jti = payload.get("jti")
    stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if not stored or stored.revoked or stored.expires_at < datetime.utcnow():
        raise invalid

    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not user.is_active:
        raise invalid

    new_access = create_access_token(subject=user.username, role=user.role.value)
    return AccessToken(access_token=new_access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    """
    Cierra la sesion: marca el refresh token como revocado (ya no sirve
    para /auth/refresh) y completa logout_at en el login_history
    correspondiente.
    """
    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        return

    jti = payload.get("jti")
    stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if stored and not stored.revoked:
        stored.revoked = True
        history = db.query(LoginHistory).filter(
            LoginHistory.session_jti == jti, LoginHistory.logout_at.is_(None)
        ).first()
        if history:
            history.logout_at = datetime.utcnow()
        db.commit()
    return
