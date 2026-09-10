"""Modelos ORM: exporta los modelos para que create_all() los registre."""
from app.models.user import User, RoleEnum
from app.models.token import RefreshToken
from app.models.login_history import LoginHistory
from app.models.matricula import Asignatura, Matricula, EstadoMatricula
