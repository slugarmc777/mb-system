# MB-System — Auth API (educativo)

Sistema de autenticacion con FastAPI: registro, login/logout con JWT (access + refresh),
roles `admin` / `usuario`, log de ingresos y cierres de sesion, bloqueo tras intentos fallidos,
y administracion completa de cuentas por parte del admin.

Sin Alembic: el control de versiones del esquema de base de datos se hace via Git/GitHub
(cada cambio de modelo se documenta en el commit correspondiente).

## 1. Instalacion

```
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y cambia `SECRET_KEY` por un valor aleatorio largo:
`python -c "import secrets; print(secrets.token_hex(32))"`

## 2. Base de datos

Las tablas se crean automaticamente al arrancar la app (`Base.metadata.create_all`
en `app/main.py`), sobre un archivo SQLite local (`mb_system.db`).

Si cambias un modelo, borra `mb_system.db` y reinicia el servidor para regenerar el esquema.

## 3. Crear el primer admin

```
python seed.py
```

Crea `admin / ChangeMe123!`. Cambia esa contrasena luego desde el endpoint de admin.

## 4. Levantar el servidor

```
uvicorn app.main:app --reload
```

Abre `http://127.0.0.1:8000/docs` para Swagger UI.

## 5. Flujo de prueba en Swagger

1. `POST /auth/register` — crea un usuario (rol `usuario` por defecto).
2. `POST /auth/login` — formulario OAuth2 (username/password). Devuelve `access_token` y `refresh_token`.
3. Boton **Authorize** — pega el `access_token`. Ahora puedes llamar endpoints protegidos.
4. `GET /users/me` — prueba que el token funciona.
5. `POST /auth/refresh` — pega el `refresh_token` para obtener un `access_token` nuevo.
6. `POST /auth/logout` — pega el `refresh_token` para cerrar la sesion (se revoca y se registra `logout_at`).
7. Con `admin`, explora `/admin/users`, `/admin/users/{id}` (PUT/DELETE) y `/admin/login-history`.

## 6. Seguridad implementada

- Hashing de contrasenas con Argon2 (via passlib).
- Access token de 15 min, refresh token de 1 dia, ambos JWT HS256.
- Refresh tokens persistidos en DB con `jti` unico y flag `revoked` para poder invalidarlos en logout.
- Bloqueo de cuenta tras 3 intentos fallidos (5 minutos, configurable en `.env`).
- Mensajes de error genericos en login (anti-enumeracion de usuarios).
- Log completo de intentos en `login_history` (IP, user-agent, timestamps, motivo de fallo).
- RBAC simple: `require_admin` protege todas las rutas bajo `/admin`.

## 7. Estructura

```
app/
  core/       -> config y seguridad (hash, JWT)
  db/         -> engine y sesion de SQLAlchemy
  models/     -> User, RefreshToken, LoginHistory
  schemas/    -> Pydantic (entrada/salida)
  routers/    -> auth, users, admin
  deps.py     -> dependencias de FastAPI (usuario actual, requiere admin)
  main.py     -> instancia FastAPI
seed.py       -> crea el admin inicial
```
