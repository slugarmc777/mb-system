"""
Punto de entrada de la aplicacion FastAPI.

Ejecutar con: uvicorn app.main:app --reload
Swagger UI queda disponible en: http://127.0.0.1:8000/docs

Sin Alembic: el esquema de base de datos se versiona junto con el codigo
en GitHub. Cada vez que agregues o cambies un modelo, borra el archivo
mb_system.db en desarrollo y vuelve a arrancar para que create_all()
genere el esquema actualizado.
"""
from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.routers import auth, users, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MB-System Auth",
    description="Sistema educativo de autenticacion, roles (admin/usuario) y log de sesiones",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def health():
    """Endpoint simple para verificar que el servidor esta arriba."""
    return {"status": "ok"}
