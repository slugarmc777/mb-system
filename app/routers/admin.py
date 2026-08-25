"""
Router de administracion. Todas las rutas requieren rol admin gracias a
`dependencies=[Depends(require_admin)]` a nivel de router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.core.security import hash_password
from app.models.user import User
from app.models.login_history import LoginHistory
from app.schemas.user import UserOut, UserAdminUpdate
from app.schemas.login_history import LoginHistoryOut

router = APIRouter(prefix="/admin", tags=["Administracion"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    """Lista todos los usuarios registrados."""
    return db.query(User).order_by(User.id).all()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de un usuario por id."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserAdminUpdate, db: Session = Depends(get_db)):
    """
    Administracion completa de la cuenta: cambiar email, rol, activar/
    desactivar, o resetear la contrasena. Solo se actualizan los campos
    enviados (el resto queda igual).
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.email is not None:
        user.email = data.email
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.new_password is not None:
        user.hashed_password = hash_password(data.new_password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    """Elimina un usuario. Un admin no puede eliminar su propia cuenta."""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return


@router.get("/login-history", response_model=list[LoginHistoryOut])
def all_login_history(db: Session = Depends(get_db)):
    """El admin puede ver el historial de sesiones de todos los usuarios."""
    return db.query(LoginHistory).order_by(LoginHistory.login_at.desc()).all()
