"""Router de usuario autenticado: perfil propio e historial propio de sesiones."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.login_history import LoginHistory
from app.schemas.user import UserOut
from app.schemas.login_history import LoginHistoryOut

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado (requiere access token valido)."""
    return current_user


@router.get("/me/login-history", response_model=list[LoginHistoryOut])
def my_login_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """El usuario solo puede ver su propio historial de logins/logouts."""
    return (
        db.query(LoginHistory)
        .filter(LoginHistory.user_id == current_user.id)
        .order_by(LoginHistory.login_at.desc())
        .all()
    )
