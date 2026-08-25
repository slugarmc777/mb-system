"""
Script de arranque: crea el usuario admin inicial si no existe.

Ejecutar una sola vez: python seed.py
"""
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, RoleEnum
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("El usuario admin ya existe.")
    else:
        admin = User(
            username="admin",
            email="admin@mbsystem.com",
            hashed_password=hash_password("Contraseña123"),
            role=RoleEnum.admin,
        )
        db.add(admin)
        db.commit()
        print("Admin creado -> usuario: admin | password: Contraseña123")
finally:
    db.close()
