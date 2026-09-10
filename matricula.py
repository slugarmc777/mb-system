"""
Esquemas Pydantic del modulo de Matricula (entrada/salida de la API).

Separan la representacion interna (modelos SQLAlchemy) de lo que viaja por
HTTP, igual que hace el modulo de autenticacion con UserCreate / UserOut.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.matricula import EstadoMatricula


# ---------- Asignatura ----------
class AsignaturaCreate(BaseModel):
    """Datos para crear una asignatura (la carga el admin/secretaria)."""
    codigo: str = Field(min_length=2, max_length=20)
    nombre: str = Field(min_length=3, max_length=120)
    creditos: int = Field(default=3, ge=1, le=10)
    cupo_maximo: int = Field(default=30, ge=1, le=200)


class AsignaturaOut(BaseModel):
    """Representacion publica de una asignatura."""
    id: int
    codigo: str
    nombre: str
    creditos: int
    cupo_maximo: int

    class Config:
        from_attributes = True


# ---------- Matricula ----------
class MatriculaCreate(BaseModel):
    """
    Datos para registrar una matricula.

    `estudiante_id` es opcional: si no se envia, se matricula al usuario
    autenticado (el propio estudiante). El admin puede matricular a otro
    estudiante enviando su id.
    """
    asignatura_id: int
    periodo: str = Field(pattern=r"^\d{4}-[12]$", examples=["2026-1"])
    estudiante_id: int | None = None


class MatriculaOut(BaseModel):
    """Representacion publica de una matricula."""
    id: int
    estudiante_id: int
    asignatura_id: int
    periodo: str
    estado: EstadoMatricula
    fecha_matricula: datetime

    class Config:
        from_attributes = True
