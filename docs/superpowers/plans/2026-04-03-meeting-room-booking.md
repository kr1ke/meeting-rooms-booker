# Система бронирования переговорок — План реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Веб-приложение для бронирования переговорных комнат в одном здании с тремя ролями пользователей, механизмом подтверждения и уведомлениями.

**Architecture:** Монорепо — Nuxt 4 фронтенд проксирует запросы к FastAPI бэкенду. PostgreSQL для хранения. Всё запускается через Docker Compose.

**Tech Stack:** Nuxt 4, Tailwind CSS, shadcn-vue, Pinia, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, JWT (httpOnly cookie)

---

## Структура файлов

### Backend (`backend/`)

```
backend/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, роутеры, CORS
│   ├── config.py                  # Настройки из env
│   ├── database.py                # AsyncSession, engine
│   ├── security.py                # JWT создание/проверка, хеширование паролей
│   ├── dependencies.py            # get_db, get_current_user, require_role
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User, Department
│   │   ├── room.py                # Room
│   │   ├── booking.py             # Booking
│   │   ├── notification.py        # Notification
│   │   └── settings.py            # BookingSettings
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                # LoginRequest, RegisterRequest, TokenResponse, UserResponse
│   │   ├── room.py                # RoomCreate, RoomUpdate, RoomResponse, AvailabilitySlot
│   │   ├── booking.py             # BookingCreate, BookingResponse
│   │   ├── user.py                # UserUpdate, UserResponse
│   │   ├── notification.py        # NotificationResponse
│   │   └── settings.py            # SettingsResponse, SettingsUpdate
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                # register, login, me
│   │   ├── rooms.py               # CRUD + availability
│   │   ├── bookings.py            # create, cancel, approve, reject, list
│   │   ├── users.py               # list, update
│   │   ├── departments.py         # list
│   │   ├── notifications.py       # list, mark_read
│   │   └── settings.py            # get, update
│   └── services/
│       ├── __init__.py
│       ├── auth.py                # register_user, authenticate_user
│       ├── booking.py             # create_booking, cancel_booking, validate_booking
│       └── notification.py        # create_notification
```

### Frontend (`frontend/`)

```
frontend/
├── Dockerfile
├── nuxt.config.ts
├── app/
│   ├── app.vue
│   ├── layouts/
│   │   ├── default.vue            # Сайдбар + хедер
│   │   └── auth.vue               # Центрированная форма
│   ├── pages/
│   │   ├── login.vue
│   │   ├── register.vue
│   │   ├── index.vue              # Дашборд
│   │   ├── rooms/
│   │   │   ├── index.vue          # Список комнат
│   │   │   └── [id].vue           # Детали + бронирование
│   │   ├── bookings.vue           # Мои брони
│   │   ├── department.vue         # Брони отдела
│   │   └── admin/
│   │       ├── rooms.vue
│   │       ├── bookings.vue
│   │       ├── users.vue
│   │       └── settings.vue
│   ├── components/
│   │   ├── ui/                    # shadcn компоненты (генерируются)
│   │   ├── layout/
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppHeader.vue
│   │   │   └── NotificationBell.vue
│   │   ├── room/
│   │   │   ├── RoomCard.vue
│   │   │   ├── RoomFilters.vue
│   │   │   └── EquipmentBadge.vue
│   │   └── booking/
│   │       ├── BookingForm.vue
│   │       ├── BookingCard.vue
│   │       └── BookingCalendar.vue
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── useRooms.ts
│   │   ├── useBookings.ts
│   │   └── useNotifications.ts
│   ├── middleware/
│   │   ├── auth.ts
│   │   └── role.ts
│   └── stores/
│       ├── auth.ts
│       └── notifications.ts
├── server/
│   └── api/
│       └── [...].ts               # Прокси к FastAPI
└── tailwind.config.ts
```

### Root

```
docker-compose.yml
.env
.gitignore
```

---

## Task 1: Инициализация проекта и Docker

**Files:**
- Create: `docker-compose.yml`
- Create: `.env`
- Create: `.gitignore`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Создать .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
.venv/

# Node
node_modules/
.nuxt/
.output/
dist/

# Env
.env

# IDE
.idea/
.vscode/

# Superpowers
.superpowers/
```

- [ ] **Step 2: Создать .env**

```env
POSTGRES_USER=booking
POSTGRES_PASSWORD=booking_secret
POSTGRES_DB=booking_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://booking:booking_secret@db:5432/booking_db
SECRET_KEY=dev-secret-key-change-in-production
BACKEND_URL=http://backend:8000
```

- [ ] **Step 3: Создать backend/requirements.txt**

```
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy[asyncio]==2.0.40
asyncpg==0.30.0
alembic==1.15.2
pydantic==2.11.1
pydantic-settings==2.9.1
python-jose[cryptography]==3.4.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
```

- [ ] **Step 4: Создать backend/app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60 * 24  # 24 часа

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Создать backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Создать backend/app/__init__.py**

Пустой файл.

- [ ] **Step 7: Создать backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 8: Инициализировать Nuxt 4 фронтенд**

```bash
cd /Users/kr1ke/www/trash/vibecode-test
npx nuxi@latest init frontend --template v4
```

- [ ] **Step 9: Создать frontend/Dockerfile**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npx", "nuxi", "dev", "--host", "0.0.0.0"]
```

- [ ] **Step 10: Создать docker-compose.yml**

```yaml
services:
  db:
    image: postgres:16-alpine
    env_file: .env
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  pgdata:
```

- [ ] **Step 11: Запустить и проверить**

```bash
docker compose up --build -d
```

Ожидаемый результат: `http://localhost:3000` — страница Nuxt, `http://localhost:8000/api/health` — `{"status": "ok"}`.

- [ ] **Step 12: Commit**

```bash
git init
git add .
git commit -m "feat: инициализация проекта — Docker Compose, FastAPI, Nuxt 4"
```

---

## Task 2: База данных и модели

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/room.py`
- Create: `backend/app/models/booking.py`
- Create: `backend/app/models/notification.py`
- Create: `backend/app/models/settings.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: Создать backend/app/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 2: Создать backend/app/models/user.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base

import enum


class UserRole(str, enum.Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="department")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.employee)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    department: Mapped[Department | None] = relationship(back_populates="users")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
```

- [ ] **Step 3: Создать backend/app/models/room.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment: Mapped[dict] = mapped_column(JSONB, default=dict)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")
```

- [ ] **Step 4: Создать backend/app/models/booking.py**

```python
import uuid
from datetime import datetime, date, time
import enum

from sqlalchemy import String, ForeignKey, DateTime, Date, Time, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SAEnum(BookingStatus), default=BookingStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="bookings")
    room: Mapped["Room"] = relationship(back_populates="bookings")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="booking")
```

- [ ] **Step 5: Создать backend/app/models/notification.py**

```python
import uuid
from datetime import datetime
import enum

from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class NotificationType(str, enum.Enum):
    booking_confirmed = "booking_confirmed"
    booking_rejected = "booking_rejected"
    booking_cancelled = "booking_cancelled"
    booking_pending = "booking_pending"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")
    booking: Mapped["Booking"] = relationship(back_populates="notifications")
```

- [ ] **Step 6: Создать backend/app/models/settings.py**

```python
import uuid

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class BookingSettings(Base):
    __tablename__ = "booking_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    max_duration_minutes: Mapped[int] = mapped_column(Integer, default=120)
    max_days_ahead: Mapped[int] = mapped_column(Integer, default=14)
    min_minutes_before_start: Mapped[int] = mapped_column(Integer, default=15)
```

- [ ] **Step 7: Создать backend/app/models/__init__.py**

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Импорт всех моделей для Alembic
from app.models.user import User, Department  # noqa: E402, F401
from app.models.room import Room  # noqa: E402, F401
from app.models.booking import Booking  # noqa: E402, F401
from app.models.notification import Notification  # noqa: E402, F401
from app.models.settings import BookingSettings  # noqa: E402, F401
```

- [ ] **Step 8: Инициализировать Alembic**

```bash
docker compose exec backend alembic init alembic
```

- [ ] **Step 9: Настроить alembic/env.py**

Заменить содержимое `backend/alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import settings
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 10: Обновить alembic.ini**

В `backend/alembic.ini` установить `sqlalchemy.url` как пустую строку (берётся из config.py):

```ini
sqlalchemy.url =
```

- [ ] **Step 11: Создать первую миграцию и применить**

```bash
docker compose exec backend alembic revision --autogenerate -m "initial tables"
docker compose exec backend alembic upgrade head
```

- [ ] **Step 12: Commit**

```bash
git add .
git commit -m "feat: модели БД и Alembic миграции"
```

---

## Task 3: Аутентификация (бэкенд)

**Files:**
- Create: `backend/app/security.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Создать backend/app/security.py**

```python
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
```

- [ ] **Step 2: Создать backend/app/schemas/auth.py**

```python
import uuid
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    department_id: uuid.UUID | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    department_id: uuid.UUID | None
    is_active: bool

    model_config = {"from_attributes": True}
```

Добавить `email-validator` в `backend/requirements.txt`.

- [ ] **Step 3: Создать backend/app/services/auth.py**

```python
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    name: str,
    department_id: uuid.UUID | None = None,
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        department_id=department_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user
```

- [ ] **Step 4: Создать backend/app/dependencies.py**

```python
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db as _get_db
from app.security import decode_access_token
from app.models.user import User, UserRole
from sqlalchemy import select


async def get_db():
    async for session in _get_db():
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    return user


def require_role(*roles: UserRole):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return current_user
    return checker
```

- [ ] **Step 5: Создать backend/app/routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.auth import get_user_by_email, create_user, authenticate_user
from app.security import create_access_token
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user = await create_user(db, data.email, data.password, data.name, data.department_id)

    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="lax", max_age=60 * 60 * 24
    )
    return user


@router.post("/login", response_model=UserResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="lax", max_age=60 * 60 * 24
    )
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "ok"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 6: Создать пустые __init__.py**

Создать пустые файлы:
- `backend/app/schemas/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/routers/__init__.py`

- [ ] **Step 7: Подключить роутер в main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Проверить вручную**

```bash
docker compose up --build -d
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User"}' -v
# В ответе должен быть Set-Cookie с access_token
```

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: аутентификация — регистрация, логин, JWT в httpOnly cookie"
```

---

## Task 4: CRUD комнат (бэкенд)

**Files:**
- Create: `backend/app/schemas/room.py`
- Create: `backend/app/routers/rooms.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Создать backend/app/schemas/room.py**

```python
import uuid
from datetime import time
from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    floor: int
    capacity: int
    equipment: dict = {}
    requires_approval: bool = False


class RoomUpdate(BaseModel):
    name: str | None = None
    floor: int | None = None
    capacity: int | None = None
    equipment: dict | None = None
    requires_approval: bool | None = None
    is_active: bool | None = None


class RoomResponse(BaseModel):
    id: uuid.UUID
    name: str
    floor: int
    capacity: int
    equipment: dict
    requires_approval: bool
    is_active: bool

    model_config = {"from_attributes": True}


class AvailabilitySlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool
    booking_title: str | None = None
```

- [ ] **Step 2: Создать backend/app/routers/rooms.py**

```python
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, AvailabilitySlot

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
async def list_rooms(
    floor: int | None = None,
    min_capacity: int | None = None,
    equipment: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Room).where(Room.is_active == True)

    if floor is not None:
        query = query.where(Room.floor == floor)
    if min_capacity is not None:
        query = query.where(Room.capacity >= min_capacity)

    result = await db.execute(query.order_by(Room.floor, Room.name))
    rooms = result.scalars().all()

    # Фильтрация по оборудованию на уровне Python (JSONB contains)
    if equipment:
        keys = [k.strip() for k in equipment.split(",")]
        rooms = [r for r in rooms if all(r.equipment.get(k) for k in keys)]

    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return room


@router.get("/{room_id}/availability", response_model=list[AvailabilitySlot])
async def get_availability(
    room_id: uuid.UUID,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Получить все активные брони на эту дату
    result = await db.execute(
        select(Booking)
        .where(
            Booking.room_id == room_id,
            Booking.date == date,
            Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        )
        .order_by(Booking.start_time)
    )
    bookings = result.scalars().all()

    # Генерация слотов с 08:00 до 20:00 с шагом 30 минут
    from datetime import time as t, timedelta, datetime as dt

    slots = []
    current = dt.combine(date, t(8, 0))
    end_of_day = dt.combine(date, t(20, 0))

    while current < end_of_day:
        slot_start = current.time()
        slot_end = (current + timedelta(minutes=30)).time()

        # Проверка пересечения с бронями
        booked = None
        for b in bookings:
            if b.start_time < slot_end and b.end_time > slot_start:
                booked = b
                break

        slots.append(AvailabilitySlot(
            start_time=slot_start,
            end_time=slot_end,
            is_available=booked is None,
            booking_title=booked.title if booked else None,
        ))
        current += timedelta(minutes=30)

    return slots


@router.post("", response_model=RoomResponse, status_code=201)
async def create_room(
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    room = Room(**data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: uuid.UUID,
    data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(room, key, value)

    await db.commit()
    await db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
async def delete_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    # Мягкое удаление
    room.is_active = False
    await db.commit()
```

- [ ] **Step 3: Подключить роутер в main.py**

Добавить:
```python
from app.routers import auth, rooms

app.include_router(auth.router)
app.include_router(rooms.router)
```

- [ ] **Step 4: Проверить и commit**

```bash
docker compose restart backend
curl -X POST http://localhost:8000/api/rooms \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<token>" \
  -d '{"name":"Переговорка 1","floor":1,"capacity":6,"equipment":{"projector":true}}'
```

```bash
git add .
git commit -m "feat: CRUD переговорок + эндпоинт доступности"
```

---

## Task 5: Бронирование (бэкенд)

**Files:**
- Create: `backend/app/schemas/booking.py`
- Create: `backend/app/services/booking.py`
- Create: `backend/app/services/notification.py`
- Create: `backend/app/routers/bookings.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Создать backend/app/schemas/booking.py**

```python
import uuid
from datetime import date, time, datetime
from pydantic import BaseModel


class BookingCreate(BaseModel):
    room_id: uuid.UUID
    title: str
    date: date
    start_time: time
    end_time: time


class BookingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    room_id: uuid.UUID
    title: str
    date: date
    start_time: time
    end_time: time
    status: str
    created_at: datetime
    user_name: str | None = None
    room_name: str | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Создать backend/app/services/notification.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType
from app.models.booking import Booking


async def create_notification(
    db: AsyncSession,
    user_id,
    booking_id,
    notification_type: NotificationType,
    message: str,
):
    notification = Notification(
        user_id=user_id,
        booking_id=booking_id,
        type=notification_type,
        message=message,
    )
    db.add(notification)
    await db.flush()
    return notification
```

- [ ] **Step 3: Создать backend/app/services/booking.py**

```python
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.settings import BookingSettings
from app.models.notification import NotificationType
from app.schemas.booking import BookingCreate
from app.services.notification import create_notification


async def get_booking_settings(db: AsyncSession) -> BookingSettings:
    result = await db.execute(select(BookingSettings))
    settings = result.scalar_one_or_none()
    if not settings:
        # Создать настройки по умолчанию
        settings = BookingSettings()
        db.add(settings)
        await db.flush()
    return settings


async def validate_and_create_booking(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: BookingCreate,
) -> Booking:
    # 1. Проверить что комната существует и активна
    result = await db.execute(select(Room).where(Room.id == data.room_id))
    room = result.scalar_one_or_none()
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Комната не найдена или неактивна")

    # 2. Проверить что время в будущем
    booking_start = datetime.combine(data.date, data.start_time)
    if booking_start <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Нельзя бронировать в прошлом")

    # 3. Проверить ограничения из настроек
    settings = await get_booking_settings(db)

    duration = (
        datetime.combine(data.date, data.end_time) - datetime.combine(data.date, data.start_time)
    )
    if duration.total_seconds() / 60 > settings.max_duration_minutes:
        raise HTTPException(
            status_code=400,
            detail=f"Максимальная длительность — {settings.max_duration_minutes} минут",
        )

    days_ahead = (data.date - datetime.utcnow().date()).days
    if days_ahead > settings.max_days_ahead:
        raise HTTPException(
            status_code=400,
            detail=f"Можно бронировать не более чем на {settings.max_days_ahead} дней вперёд",
        )

    minutes_before = (booking_start - datetime.utcnow()).total_seconds() / 60
    if minutes_before < settings.min_minutes_before_start:
        raise HTTPException(
            status_code=400,
            detail=f"Бронь должна быть создана минимум за {settings.min_minutes_before_start} минут до начала",
        )

    # 4. Проверить пересечения
    result = await db.execute(
        select(Booking).where(
            and_(
                Booking.room_id == data.room_id,
                Booking.date == data.date,
                Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
                Booking.start_time < data.end_time,
                Booking.end_time > data.start_time,
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Время уже занято")

    # 5. Определить статус
    status = BookingStatus.pending if room.requires_approval else BookingStatus.confirmed

    booking = Booking(
        user_id=user_id,
        room_id=data.room_id,
        title=data.title,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        status=status,
    )
    db.add(booking)
    await db.flush()

    # 6. Уведомление
    if status == BookingStatus.confirmed:
        msg = f"Бронь «{data.title}» в {room.name} подтверждена"
        ntype = NotificationType.booking_confirmed
    else:
        msg = f"Бронь «{data.title}» в {room.name} ожидает подтверждения"
        ntype = NotificationType.booking_pending

    await create_notification(db, user_id, booking.id, ntype, msg)
    await db.commit()
    await db.refresh(booking)

    return booking
```

- [ ] **Step 4: Создать backend/app/routers/bookings.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_user, require_role
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.models.notification import NotificationType
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking import validate_and_create_booking
from app.services.notification import create_notification

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


def booking_to_response(b: Booking) -> BookingResponse:
    return BookingResponse(
        id=b.id,
        user_id=b.user_id,
        room_id=b.room_id,
        title=b.title,
        date=b.date,
        start_time=b.start_time,
        end_time=b.end_time,
        status=b.status.value,
        created_at=b.created_at,
        user_name=b.user.name if b.user else None,
        room_name=b.room.name if b.room else None,
    )


@router.get("", response_model=list[BookingResponse])
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.date.desc(), Booking.start_time.desc())
    )
    return [booking_to_response(b) for b in result.scalars().all()]


@router.get("/department", response_model=list[BookingResponse])
async def department_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.manager, UserRole.admin)),
):
    result = await db.execute(
        select(Booking)
        .join(User)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(User.department_id == current_user.department_id)
        .order_by(Booking.date.desc(), Booking.start_time.desc())
    )
    return [booking_to_response(b) for b in result.scalars().all()]


@router.get("/all", response_model=list[BookingResponse])
async def all_bookings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .order_by(Booking.date.desc(), Booking.start_time.desc())
    )
    return [booking_to_response(b) for b in result.scalars().all()]


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = await validate_and_create_booking(db, current_user.id, data)
    # Перезагрузить с relationship
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(Booking.id == booking.id)
    )
    return booking_to_response(result.scalar_one())


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")

    # Отменить может владелец или админ
    if booking.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if booking.status in (BookingStatus.cancelled, BookingStatus.rejected):
        raise HTTPException(status_code=400, detail="Бронь уже отменена или отклонена")

    booking.status = BookingStatus.cancelled
    await create_notification(
        db, booking.user_id, booking.id,
        NotificationType.booking_cancelled,
        f"Бронь «{booking.title}» в {booking.room.name} отменена",
    )
    await db.commit()
    await db.refresh(booking)
    return booking_to_response(booking)


@router.patch("/{booking_id}/approve", response_model=BookingResponse)
async def approve_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Бронь не в статусе ожидания")

    booking.status = BookingStatus.confirmed
    await create_notification(
        db, booking.user_id, booking.id,
        NotificationType.booking_confirmed,
        f"Бронь «{booking.title}» в {booking.room.name} подтверждена администратором",
    )
    await db.commit()
    await db.refresh(booking)
    return booking_to_response(booking)


@router.patch("/{booking_id}/reject", response_model=BookingResponse)
async def reject_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.user), selectinload(Booking.room))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Бронь не в статусе ожидания")

    booking.status = BookingStatus.rejected
    await create_notification(
        db, booking.user_id, booking.id,
        NotificationType.booking_rejected,
        f"Бронь «{booking.title}» в {booking.room.name} отклонена администратором",
    )
    await db.commit()
    await db.refresh(booking)
    return booking_to_response(booking)
```

- [ ] **Step 5: Подключить роутер в main.py и commit**

Добавить `from app.routers import auth, rooms, bookings` и `app.include_router(bookings.router)`.

```bash
git add .
git commit -m "feat: бронирование — создание, отмена, подтверждение, отклонение"
```

---

## Task 6: Пользователи, отделы, уведомления, настройки (бэкенд)

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/notification.py`
- Create: `backend/app/schemas/settings.py`
- Create: `backend/app/routers/users.py`
- Create: `backend/app/routers/departments.py`
- Create: `backend/app/routers/notifications.py`
- Create: `backend/app/routers/settings.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Создать backend/app/schemas/user.py**

```python
import uuid
from pydantic import BaseModel


class UserUpdate(BaseModel):
    role: str | None = None
    department_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserListResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    department_id: uuid.UUID | None
    is_active: bool

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Создать backend/app/schemas/notification.py**

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    message: str
    is_read: bool
    booking_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Создать backend/app/schemas/settings.py**

```python
from pydantic import BaseModel


class SettingsResponse(BaseModel):
    max_duration_minutes: int
    max_days_ahead: int
    min_minutes_before_start: int

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    max_duration_minutes: int | None = None
    max_days_ahead: int | None = None
    min_minutes_before_start: int | None = None
```

- [ ] **Step 4: Создать backend/app/routers/users.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, UserListResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserListResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(User).order_by(User.name))
    return result.scalars().all()


@router.patch("/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user
```

- [ ] **Step 5: Создать backend/app/routers/departments.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import Department, User

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Department).order_by(Department.name))
    departments = result.scalars().all()
    return [{"id": d.id, "name": d.name} for d in departments]
```

- [ ] **Step 6: Создать backend/app/routers/notifications.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    notification.is_read = True
    await db.commit()
    return {"detail": "ok"}
```

- [ ] **Step 7: Создать backend/app/routers/settings.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models.settings import BookingSettings
from app.models.user import User, UserRole
from app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(BookingSettings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = BookingSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(BookingSettings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = BookingSettings()
        db.add(settings)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)
    return settings
```

- [ ] **Step 8: Подключить все роутеры в main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, bookings, users, departments, notifications, settings

app = FastAPI(title="Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(notifications.router)
app.include_router(settings.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: API пользователей, отделов, уведомлений и настроек"
```

---

## Task 7: Сид данных

**Files:**
- Create: `backend/app/seed.py`

- [ ] **Step 1: Создать backend/app/seed.py**

Скрипт для заполнения БД тестовыми данными: отделы, пользователи (admin, manager, employee), комнаты.

```python
import asyncio
import uuid
from app.database import async_session
from app.models.user import Department, User, UserRole
from app.models.room import Room
from app.models.settings import BookingSettings
from app.security import hash_password
from sqlalchemy import select


async def seed():
    async with async_session() as db:
        # Проверить что БД пуста
        result = await db.execute(select(User))
        if result.scalar_one_or_none():
            print("БД уже заполнена, пропускаю")
            return

        # Отделы
        dev = Department(name="Разработка")
        marketing = Department(name="Маркетинг")
        hr = Department(name="HR")
        db.add_all([dev, marketing, hr])
        await db.flush()

        # Пользователи
        admin = User(
            email="admin@company.com",
            password_hash=hash_password("admin123"),
            name="Администратор",
            role=UserRole.admin,
            department_id=dev.id,
        )
        manager = User(
            email="manager@company.com",
            password_hash=hash_password("manager123"),
            name="Менеджер Разработки",
            role=UserRole.manager,
            department_id=dev.id,
        )
        employee = User(
            email="user@company.com",
            password_hash=hash_password("user123"),
            name="Иван Петров",
            role=UserRole.employee,
            department_id=marketing.id,
        )
        db.add_all([admin, manager, employee])

        # Комнаты
        rooms = [
            Room(name="Альфа", floor=1, capacity=4, equipment={"whiteboard": True}),
            Room(name="Бета", floor=1, capacity=8, equipment={"projector": True, "whiteboard": True}),
            Room(name="Гамма", floor=2, capacity=12, equipment={"projector": True, "videoconference": True}, requires_approval=True),
            Room(name="Дельта", floor=2, capacity=4, equipment={}),
            Room(name="Эпсилон", floor=3, capacity=20, equipment={"projector": True, "videoconference": True, "whiteboard": True}, requires_approval=True),
        ]
        db.add_all(rooms)

        # Настройки
        settings = BookingSettings(
            max_duration_minutes=120,
            max_days_ahead=14,
            min_minutes_before_start=15,
        )
        db.add(settings)

        await db.commit()
        print("Сид данных выполнен успешно")


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 2: Запустить сид**

```bash
docker compose exec backend python -m app.seed
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: сид данных — отделы, пользователи, комнаты"
```

---

## Task 8: Nuxt — настройка Tailwind, shadcn, прокси

**Files:**
- Modify: `frontend/nuxt.config.ts`
- Create: `frontend/server/api/[...].ts`
- Modify: `frontend/app/app.vue`

- [ ] **Step 1: Установить зависимости**

```bash
docker compose exec frontend npm install -D @nuxtjs/tailwindcss
docker compose exec frontend npx shadcn-vue@latest init
```

При инициализации shadcn-vue выбрать:
- Style: Default
- Base color: Slate
- CSS variables: Yes

- [ ] **Step 2: Настроить nuxt.config.ts**

```typescript
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    'shadcn-nuxt',
    '@pinia/nuxt',
  ],
  shadcn: {
    prefix: '',
    componentDir: './app/components/ui',
  },
  runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
  },
  compatibilityDate: '2025-01-01',
})
```

- [ ] **Step 3: Установить Pinia**

```bash
docker compose exec frontend npm install pinia @pinia/nuxt
```

- [ ] **Step 4: Настроить синий акцент в CSS**

В `frontend/app/assets/css/tailwind.css` (или где shadcn создал стили) обновить CSS-переменные:

```css
:root {
  --primary: 221.2 83.2% 53.3%;        /* Синий */
  --primary-foreground: 210 40% 98%;
  --ring: 221.2 83.2% 53.3%;
}

.dark {
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --ring: 224.3 76.3% 48%;
}
```

- [ ] **Step 5: Создать серверный прокси frontend/server/api/[...].ts**

```typescript
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const path = event.path

  // Проксировать все /api/* запросы на бэкенд
  const target = `${config.backendUrl}${path}`

  return proxyRequest(event, target)
})
```

- [ ] **Step 6: Добавить базовые shadcn компоненты**

```bash
docker compose exec frontend npx shadcn-vue@latest add button card input label badge dialog select separator avatar dropdown-menu sheet table tabs toast
```

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: настройка Tailwind, shadcn-vue (синий акцент), Pinia, прокси"
```

---

## Task 9: Фронтенд — composables и stores

**Files:**
- Create: `frontend/app/stores/auth.ts`
- Create: `frontend/app/stores/notifications.ts`
- Create: `frontend/app/composables/useAuth.ts`
- Create: `frontend/app/composables/useRooms.ts`
- Create: `frontend/app/composables/useBookings.ts`
- Create: `frontend/app/composables/useNotifications.ts`

- [ ] **Step 1: Создать frontend/app/stores/auth.ts**

```typescript
import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  name: string
  role: 'employee' | 'manager' | 'admin'
  department_id: string | null
  is_active: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: true,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => state.user?.role === 'manager',
  },
  actions: {
    setUser(user: User | null) {
      this.user = user
      this.loading = false
    },
  },
})
```

- [ ] **Step 2: Создать frontend/app/stores/notifications.ts**

```typescript
import { defineStore } from 'pinia'

interface Notification {
  id: string
  type: string
  message: string
  is_read: boolean
  booking_id: string
  created_at: string
}

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [] as Notification[],
  }),
  getters: {
    unreadCount: (state) => state.items.filter(n => !n.is_read).length,
  },
  actions: {
    setItems(items: Notification[]) {
      this.items = items
    },
    markAsRead(id: string) {
      const item = this.items.find(n => n.id === id)
      if (item) item.is_read = true
    },
  },
})
```

- [ ] **Step 3: Создать frontend/app/composables/useAuth.ts**

```typescript
export function useAuth() {
  const store = useAuthStore()

  async function login(email: string, password: string) {
    const data = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    store.setUser(data)
    return data
  }

  async function register(email: string, password: string, name: string, departmentId?: string) {
    const data = await $fetch('/api/auth/register', {
      method: 'POST',
      body: { email, password, name, department_id: departmentId },
    })
    store.setUser(data)
    return data
  }

  async function fetchMe() {
    try {
      const data = await $fetch('/api/auth/me')
      store.setUser(data)
    } catch {
      store.setUser(null)
    }
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    store.setUser(null)
    navigateTo('/login')
  }

  return { login, register, fetchMe, logout, store }
}
```

- [ ] **Step 4: Создать frontend/app/composables/useRooms.ts**

```typescript
interface Room {
  id: string
  name: string
  floor: number
  capacity: number
  equipment: Record<string, boolean>
  requires_approval: boolean
  is_active: boolean
}

interface AvailabilitySlot {
  start_time: string
  end_time: string
  is_available: boolean
  booking_title: string | null
}

export function useRooms() {
  async function fetchRooms(params?: { floor?: number; min_capacity?: number; equipment?: string }) {
    return await $fetch<Room[]>('/api/rooms', { params })
  }

  async function fetchRoom(id: string) {
    return await $fetch<Room>(`/api/rooms/${id}`)
  }

  async function fetchAvailability(roomId: string, date: string) {
    return await $fetch<AvailabilitySlot[]>(`/api/rooms/${roomId}/availability`, {
      params: { date },
    })
  }

  async function createRoom(data: Partial<Room>) {
    return await $fetch<Room>('/api/rooms', { method: 'POST', body: data })
  }

  async function updateRoom(id: string, data: Partial<Room>) {
    return await $fetch<Room>(`/api/rooms/${id}`, { method: 'PUT', body: data })
  }

  async function deleteRoom(id: string) {
    return await $fetch(`/api/rooms/${id}`, { method: 'DELETE' })
  }

  return { fetchRooms, fetchRoom, fetchAvailability, createRoom, updateRoom, deleteRoom }
}
```

- [ ] **Step 5: Создать frontend/app/composables/useBookings.ts**

```typescript
interface Booking {
  id: string
  user_id: string
  room_id: string
  title: string
  date: string
  start_time: string
  end_time: string
  status: string
  created_at: string
  user_name: string | null
  room_name: string | null
}

interface BookingCreate {
  room_id: string
  title: string
  date: string
  start_time: string
  end_time: string
}

export function useBookings() {
  async function fetchMyBookings() {
    return await $fetch<Booking[]>('/api/bookings')
  }

  async function fetchDepartmentBookings() {
    return await $fetch<Booking[]>('/api/bookings/department')
  }

  async function fetchAllBookings() {
    return await $fetch<Booking[]>('/api/bookings/all')
  }

  async function createBooking(data: BookingCreate) {
    return await $fetch<Booking>('/api/bookings', { method: 'POST', body: data })
  }

  async function cancelBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/cancel`, { method: 'PATCH' })
  }

  async function approveBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/approve`, { method: 'PATCH' })
  }

  async function rejectBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/reject`, { method: 'PATCH' })
  }

  return {
    fetchMyBookings, fetchDepartmentBookings, fetchAllBookings,
    createBooking, cancelBooking, approveBooking, rejectBooking,
  }
}
```

- [ ] **Step 6: Создать frontend/app/composables/useNotifications.ts**

```typescript
export function useNotifications() {
  const store = useNotificationsStore()

  async function fetchNotifications() {
    const data = await $fetch<any[]>('/api/notifications')
    store.setItems(data)
    return data
  }

  async function markAsRead(id: string) {
    await $fetch(`/api/notifications/${id}/read`, { method: 'PATCH' })
    store.markAsRead(id)
  }

  return { fetchNotifications, markAsRead, store }
}
```

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: composables и stores для auth, rooms, bookings, notifications"
```

---

## Task 10: Фронтенд — middleware и layouts

**Files:**
- Create: `frontend/app/middleware/auth.ts`
- Create: `frontend/app/middleware/role.ts`
- Create: `frontend/app/layouts/default.vue`
- Create: `frontend/app/layouts/auth.vue`
- Create: `frontend/app/components/layout/AppSidebar.vue`
- Create: `frontend/app/components/layout/AppHeader.vue`
- Create: `frontend/app/components/layout/NotificationBell.vue`

- [ ] **Step 1: Создать frontend/app/middleware/auth.ts**

```typescript
export default defineNuxtRouteMiddleware(async (to) => {
  const { fetchMe, store } = useAuth()

  if (store.loading) {
    await fetchMe()
  }

  if (!store.isAuthenticated && to.path !== '/login' && to.path !== '/register') {
    return navigateTo('/login')
  }

  if (store.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    return navigateTo('/')
  }
})
```

- [ ] **Step 2: Создать frontend/app/middleware/role.ts**

```typescript
export default defineNuxtRouteMiddleware((to) => {
  const { store } = useAuth()

  // Страницы админа
  if (to.path.startsWith('/admin') && !store.isAdmin) {
    return navigateTo('/')
  }

  // Страница менеджера
  if (to.path === '/department' && !store.isManager && !store.isAdmin) {
    return navigateTo('/')
  }
})
```

- [ ] **Step 3: Создать frontend/app/components/layout/NotificationBell.vue**

```vue
<script setup lang="ts">
const { fetchNotifications, markAsRead, store } = useNotifications()

const open = ref(false)

onMounted(() => {
  fetchNotifications()
  // Обновлять каждые 30 секунд
  setInterval(fetchNotifications, 30000)
})
</script>

<template>
  <DropdownMenu v-model:open="open">
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" size="icon" class="relative">
        <BellIcon class="h-5 w-5" />
        <span
          v-if="store.unreadCount > 0"
          class="absolute -top-1 -right-1 bg-primary text-primary-foreground text-xs rounded-full h-5 w-5 flex items-center justify-center"
        >
          {{ store.unreadCount }}
        </span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-80">
      <div class="p-2 font-semibold text-sm">Уведомления</div>
      <Separator />
      <div v-if="store.items.length === 0" class="p-4 text-sm text-muted-foreground text-center">
        Нет уведомлений
      </div>
      <DropdownMenuItem
        v-for="n in store.items.slice(0, 10)"
        :key="n.id"
        class="flex flex-col items-start gap-1 p-3"
        :class="{ 'opacity-50': n.is_read }"
        @click="markAsRead(n.id)"
      >
        <span class="text-sm">{{ n.message }}</span>
        <span class="text-xs text-muted-foreground">{{ new Date(n.created_at).toLocaleString('ru') }}</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
```

Примечание: `BellIcon` — использовать `lucide-vue-next`. Установить: `npm install lucide-vue-next`.

- [ ] **Step 4: Создать frontend/app/components/layout/AppSidebar.vue**

```vue
<script setup lang="ts">
import {
  LayoutDashboard, DoorOpen, CalendarDays, Building2, Settings, Users, ShieldCheck
} from 'lucide-vue-next'

const { store } = useAuth()
const route = useRoute()

const mainLinks = [
  { to: '/', label: 'Дашборд', icon: LayoutDashboard },
  { to: '/rooms', label: 'Переговорки', icon: DoorOpen },
  { to: '/bookings', label: 'Мои брони', icon: CalendarDays },
]

const managerLinks = [
  { to: '/department', label: 'Брони отдела', icon: Building2 },
]

const adminLinks = [
  { to: '/admin/rooms', label: 'Управление комнатами', icon: DoorOpen },
  { to: '/admin/bookings', label: 'Все брони', icon: CalendarDays },
  { to: '/admin/users', label: 'Пользователи', icon: Users },
  { to: '/admin/settings', label: 'Настройки', icon: Settings },
]
</script>

<template>
  <aside class="w-64 border-r bg-card min-h-screen p-4 flex flex-col">
    <div class="flex items-center gap-2 mb-8 px-2">
      <ShieldCheck class="h-8 w-8 text-primary" />
      <span class="text-lg font-bold">BookRoom</span>
    </div>

    <nav class="flex-1 space-y-1">
      <NuxtLink
        v-for="link in mainLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
        :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
      >
        <component :is="link.icon" class="h-4 w-4" />
        {{ link.label }}
      </NuxtLink>

      <template v-if="store.isManager || store.isAdmin">
        <Separator class="my-4" />
        <div class="px-3 text-xs font-medium text-muted-foreground mb-2">Менеджер</div>
        <NuxtLink
          v-for="link in managerLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
          :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
        >
          <component :is="link.icon" class="h-4 w-4" />
          {{ link.label }}
        </NuxtLink>
      </template>

      <template v-if="store.isAdmin">
        <Separator class="my-4" />
        <div class="px-3 text-xs font-medium text-muted-foreground mb-2">Администратор</div>
        <NuxtLink
          v-for="link in adminLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
          :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
        >
          <component :is="link.icon" class="h-4 w-4" />
          {{ link.label }}
        </NuxtLink>
      </template>
    </nav>
  </aside>
</template>
```

- [ ] **Step 5: Создать frontend/app/components/layout/AppHeader.vue**

```vue
<script setup lang="ts">
import { LogOut } from 'lucide-vue-next'

const { logout, store } = useAuth()
</script>

<template>
  <header class="h-16 border-b bg-card px-6 flex items-center justify-between">
    <div />
    <div class="flex items-center gap-4">
      <NotificationBell />
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="flex items-center gap-2">
            <Avatar class="h-8 w-8">
              <AvatarFallback>{{ store.user?.name?.charAt(0) }}</AvatarFallback>
            </Avatar>
            <span class="text-sm">{{ store.user?.name }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem @click="logout" class="text-destructive">
            <LogOut class="h-4 w-4 mr-2" />
            Выйти
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>
```

- [ ] **Step 6: Создать frontend/app/layouts/auth.vue**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <slot />
  </div>
</template>
```

- [ ] **Step 7: Создать frontend/app/layouts/default.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })
</script>

<template>
  <div class="flex min-h-screen bg-background">
    <AppSidebar />
    <div class="flex-1 flex flex-col">
      <AppHeader />
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
```

- [ ] **Step 8: Обновить frontend/app/app.vue**

```vue
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
```

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: middleware auth/role, layouts, сайдбар, хедер, уведомления"
```

---

## Task 11: Фронтенд — страницы авторизации

**Files:**
- Create: `frontend/app/pages/login.vue`
- Create: `frontend/app/pages/register.vue`

- [ ] **Step 1: Создать frontend/app/pages/login.vue**

```vue
<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { login } = useAuth()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-md">
    <CardHeader class="text-center">
      <CardTitle class="text-2xl">Вход</CardTitle>
      <CardDescription>Введите email и пароль</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="email" type="email" placeholder="email@company.com" required />
        </div>
        <div class="space-y-2">
          <Label for="password">Пароль</Label>
          <Input id="password" v-model="password" type="password" required />
        </div>
        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </Button>
      </form>
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Нет аккаунта?
        <NuxtLink to="/register" class="text-primary hover:underline">Зарегистрироваться</NuxtLink>
      </p>
    </CardContent>
  </Card>
</template>
```

- [ ] **Step 2: Создать frontend/app/pages/register.vue**

```vue
<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { register } = useAuth()
const name = ref('')
const email = ref('')
const password = ref('')
const departmentId = ref<string>()
const departments = ref<{ id: string; name: string }[]>([])
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
    departments.value = await $fetch('/api/departments')
  } catch {}
})

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await register(email.value, password.value, name.value, departmentId.value)
    navigateTo('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-md">
    <CardHeader class="text-center">
      <CardTitle class="text-2xl">Регистрация</CardTitle>
      <CardDescription>Создайте аккаунт</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label for="name">Имя</Label>
          <Input id="name" v-model="name" placeholder="Иван Петров" required />
        </div>
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="email" type="email" placeholder="email@company.com" required />
        </div>
        <div class="space-y-2">
          <Label for="password">Пароль</Label>
          <Input id="password" v-model="password" type="password" required />
        </div>
        <div class="space-y-2">
          <Label for="department">Отдел</Label>
          <Select v-model="departmentId">
            <SelectTrigger>
              <SelectValue placeholder="Выберите отдел" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="d in departments" :key="d.id" :value="d.id">
                {{ d.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </Button>
      </form>
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Уже есть аккаунт?
        <NuxtLink to="/login" class="text-primary hover:underline">Войти</NuxtLink>
      </p>
    </CardContent>
  </Card>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: страницы логина и регистрации"
```

---

## Task 12: Фронтенд — дашборд и компоненты комнат

**Files:**
- Create: `frontend/app/pages/index.vue`
- Create: `frontend/app/components/room/EquipmentBadge.vue`
- Create: `frontend/app/components/room/RoomCard.vue`
- Create: `frontend/app/components/room/RoomFilters.vue`
- Create: `frontend/app/components/booking/BookingCard.vue`

- [ ] **Step 1: Создать frontend/app/components/room/EquipmentBadge.vue**

```vue
<script setup lang="ts">
import { Monitor, Presentation, Video } from 'lucide-vue-next'

const props = defineProps<{ type: string }>()

const config: Record<string, { label: string; icon: any }> = {
  projector: { label: 'Проектор', icon: Presentation },
  whiteboard: { label: 'Доска', icon: Monitor },
  videoconference: { label: 'Видеоконференция', icon: Video },
}

const item = computed(() => config[props.type] || { label: props.type, icon: Monitor })
</script>

<template>
  <Badge variant="secondary" class="flex items-center gap-1">
    <component :is="item.icon" class="h-3 w-3" />
    {{ item.label }}
  </Badge>
</template>
```

- [ ] **Step 2: Создать frontend/app/components/room/RoomCard.vue**

```vue
<script setup lang="ts">
import { Users, MapPin } from 'lucide-vue-next'

const props = defineProps<{
  room: {
    id: string
    name: string
    floor: number
    capacity: number
    equipment: Record<string, boolean>
    requires_approval: boolean
  }
}>()
</script>

<template>
  <Card class="hover:border-primary/50 transition-colors cursor-pointer" @click="navigateTo(`/rooms/${room.id}`)">
    <CardHeader>
      <div class="flex items-center justify-between">
        <CardTitle class="text-lg">{{ room.name }}</CardTitle>
        <Badge v-if="room.requires_approval" variant="outline" class="text-xs">Требует подтверждения</Badge>
      </div>
    </CardHeader>
    <CardContent>
      <div class="flex items-center gap-4 text-sm text-muted-foreground mb-3">
        <span class="flex items-center gap-1"><MapPin class="h-4 w-4" /> Этаж {{ room.floor }}</span>
        <span class="flex items-center gap-1"><Users class="h-4 w-4" /> до {{ room.capacity }} чел.</span>
      </div>
      <div class="flex flex-wrap gap-1">
        <EquipmentBadge v-for="(val, key) in room.equipment" :key="key" v-show="val" :type="String(key)" />
      </div>
    </CardContent>
  </Card>
</template>
```

- [ ] **Step 3: Создать frontend/app/components/room/RoomFilters.vue**

```vue
<script setup lang="ts">
const emit = defineEmits<{
  filter: [params: { floor?: number; min_capacity?: number; equipment?: string }]
}>()

const floor = ref<string>()
const minCapacity = ref<string>()
const equipment = ref<string[]>([])

function applyFilters() {
  emit('filter', {
    floor: floor.value ? Number(floor.value) : undefined,
    min_capacity: minCapacity.value ? Number(minCapacity.value) : undefined,
    equipment: equipment.value.length ? equipment.value.join(',') : undefined,
  })
}

watch([floor, minCapacity, equipment], applyFilters, { deep: true })
</script>

<template>
  <div class="flex flex-wrap items-center gap-4">
    <Select v-model="floor">
      <SelectTrigger class="w-36">
        <SelectValue placeholder="Этаж" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">Все этажи</SelectItem>
        <SelectItem v-for="f in [1, 2, 3]" :key="f" :value="String(f)">Этаж {{ f }}</SelectItem>
      </SelectContent>
    </Select>

    <Select v-model="minCapacity">
      <SelectTrigger class="w-44">
        <SelectValue placeholder="Вместимость" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">Любая</SelectItem>
        <SelectItem value="4">от 4 человек</SelectItem>
        <SelectItem value="8">от 8 человек</SelectItem>
        <SelectItem value="12">от 12 человек</SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
```

- [ ] **Step 4: Создать frontend/app/components/booking/BookingCard.vue**

```vue
<script setup lang="ts">
import { Clock, MapPin } from 'lucide-vue-next'

const props = defineProps<{
  booking: {
    id: string
    title: string
    date: string
    start_time: string
    end_time: string
    status: string
    room_name: string | null
  }
  showCancel?: boolean
  showActions?: boolean
}>()

const emit = defineEmits<{
  cancel: [id: string]
  approve: [id: string]
  reject: [id: string]
}>()

const statusColors: Record<string, string> = {
  confirmed: 'bg-green-100 text-green-800',
  pending: 'bg-yellow-100 text-yellow-800',
  rejected: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
}

const statusLabels: Record<string, string> = {
  confirmed: 'Подтверждена',
  pending: 'Ожидает',
  rejected: 'Отклонена',
  cancelled: 'Отменена',
}
</script>

<template>
  <Card>
    <CardContent class="p-4">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="font-medium">{{ booking.title }}</h3>
          <div class="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
            <span class="flex items-center gap-1"><MapPin class="h-3 w-3" /> {{ booking.room_name }}</span>
            <span class="flex items-center gap-1">
              <Clock class="h-3 w-3" />
              {{ booking.date }} {{ booking.start_time.slice(0, 5) }}–{{ booking.end_time.slice(0, 5) }}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2 py-1 rounded-full" :class="statusColors[booking.status]">
            {{ statusLabels[booking.status] }}
          </span>
        </div>
      </div>
      <div v-if="showCancel || showActions" class="mt-3 flex gap-2">
        <Button
          v-if="showCancel && (booking.status === 'confirmed' || booking.status === 'pending')"
          variant="outline" size="sm"
          @click="emit('cancel', booking.id)"
        >
          Отменить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          size="sm"
          @click="emit('approve', booking.id)"
        >
          Подтвердить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          variant="destructive" size="sm"
          @click="emit('reject', booking.id)"
        >
          Отклонить
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
```

- [ ] **Step 5: Создать frontend/app/pages/index.vue (дашборд)**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const { store } = useAuth()
const { fetchMyBookings } = useBookings()

const bookings = ref<any[]>([])

onMounted(async () => {
  const all = await fetchMyBookings()
  // Показать только предстоящие
  const today = new Date().toISOString().split('T')[0]
  bookings.value = all.filter(b =>
    b.date >= today && (b.status === 'confirmed' || b.status === 'pending')
  ).slice(0, 5)
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Привет, {{ store.user?.name }}!</h1>

    <div class="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Ближайшие брони</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="bookings.length === 0" class="text-muted-foreground text-sm">
            У вас нет предстоящих бронирований
          </div>
          <div class="space-y-3">
            <BookingCard v-for="b in bookings" :key="b.id" :booking="b" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Быстрое бронирование</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground text-sm mb-4">Найдите свободную переговорку</p>
          <Button @click="navigateTo('/rooms')" class="w-full">Смотреть переговорки</Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
```

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: дашборд, компоненты RoomCard, RoomFilters, BookingCard, EquipmentBadge"
```

---

## Task 13: Фронтенд — страницы комнат и бронирования

**Files:**
- Create: `frontend/app/pages/rooms/index.vue`
- Create: `frontend/app/pages/rooms/[id].vue`
- Create: `frontend/app/components/booking/BookingForm.vue`
- Create: `frontend/app/components/booking/BookingCalendar.vue`
- Create: `frontend/app/pages/bookings.vue`

- [ ] **Step 1: Создать frontend/app/pages/rooms/index.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const { fetchRooms } = useRooms()
const rooms = ref<any[]>([])
const loading = ref(true)

async function loadRooms(params?: any) {
  loading.value = true
  rooms.value = await fetchRooms(params)
  loading.value = false
}

onMounted(() => loadRooms())
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Переговорки</h1>
    <RoomFilters @filter="loadRooms" class="mb-6" />
    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>
    <div v-if="!loading && rooms.length === 0" class="text-muted-foreground">
      Нет комнат по выбранным фильтрам
    </div>
  </div>
</template>
```

- [ ] **Step 2: Создать frontend/app/components/booking/BookingCalendar.vue**

Компонент для отображения слотов доступности на выбранную дату.

```vue
<script setup lang="ts">
const props = defineProps<{
  slots: {
    start_time: string
    end_time: string
    is_available: boolean
    booking_title: string | null
  }[]
}>()

const emit = defineEmits<{
  selectSlot: [startTime: string, endTime: string]
}>()

const selectedStart = ref<string | null>(null)
const selectedEnd = ref<string | null>(null)

function toggleSlot(slot: typeof props.slots[0]) {
  if (!slot.is_available) return

  if (!selectedStart.value || selectedEnd.value) {
    // Начать новый выбор
    selectedStart.value = slot.start_time
    selectedEnd.value = slot.end_time
    emit('selectSlot', selectedStart.value, selectedEnd.value)
  } else {
    // Расширить выбор
    if (slot.start_time >= selectedStart.value) {
      selectedEnd.value = slot.end_time
      emit('selectSlot', selectedStart.value, selectedEnd.value)
    } else {
      selectedStart.value = slot.start_time
      emit('selectSlot', selectedStart.value, selectedEnd.value!)
    }
  }
}

function isSelected(slot: typeof props.slots[0]) {
  if (!selectedStart.value || !selectedEnd.value) return false
  return slot.start_time >= selectedStart.value && slot.end_time <= selectedEnd.value
}
</script>

<template>
  <div class="grid grid-cols-4 gap-1">
    <button
      v-for="slot in slots"
      :key="slot.start_time"
      class="p-2 text-xs rounded border text-center transition-colors"
      :class="{
        'bg-primary text-primary-foreground': isSelected(slot),
        'hover:bg-accent cursor-pointer': slot.is_available && !isSelected(slot),
        'bg-muted text-muted-foreground cursor-not-allowed': !slot.is_available,
      }"
      :disabled="!slot.is_available"
      @click="toggleSlot(slot)"
    >
      {{ slot.start_time.slice(0, 5) }}
      <span v-if="!slot.is_available" class="block text-[10px]">занято</span>
    </button>
  </div>
</template>
```

- [ ] **Step 3: Создать frontend/app/components/booking/BookingForm.vue**

```vue
<script setup lang="ts">
const props = defineProps<{ roomId: string; roomName: string }>()

const { createBooking } = useBookings()
const { fetchAvailability } = useRooms()

const title = ref('')
const date = ref(new Date().toISOString().split('T')[0])
const startTime = ref('')
const endTime = ref('')
const slots = ref<any[]>([])
const error = ref('')
const loading = ref(false)
const success = ref(false)

async function loadSlots() {
  if (!date.value) return
  slots.value = await fetchAvailability(props.roomId, date.value)
}

watch(date, loadSlots, { immediate: true })

function onSlotSelect(start: string, end: string) {
  startTime.value = start
  endTime.value = end
}

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await createBooking({
      room_id: props.roomId,
      title: title.value,
      date: date.value,
      start_time: startTime.value,
      end_time: endTime.value,
    })
    success.value = true
    title.value = ''
    startTime.value = ''
    endTime.value = ''
    await loadSlots()
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка бронирования'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Забронировать {{ roomName }}</CardTitle>
    </CardHeader>
    <CardContent>
      <div v-if="success" class="p-4 bg-green-50 text-green-800 rounded-md mb-4">
        Бронирование создано!
        <Button variant="link" size="sm" @click="success = false">Создать ещё</Button>
      </div>

      <form v-else @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label>Название встречи</Label>
          <Input v-model="title" placeholder="Стендап команды" required />
        </div>

        <div class="space-y-2">
          <Label>Дата</Label>
          <Input v-model="date" type="date" required />
        </div>

        <div class="space-y-2">
          <Label>Выберите время (клик для начала, повторный клик для конца)</Label>
          <BookingCalendar :slots="slots" @selectSlot="onSlotSelect" />
        </div>

        <div v-if="startTime && endTime" class="text-sm text-muted-foreground">
          Выбрано: {{ startTime.slice(0, 5) }} – {{ endTime.slice(0, 5) }}
        </div>

        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>

        <Button type="submit" class="w-full" :disabled="loading || !startTime || !endTime">
          {{ loading ? 'Бронирование...' : 'Забронировать' }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
```

- [ ] **Step 4: Создать frontend/app/pages/rooms/[id].vue**

```vue
<script setup lang="ts">
import { MapPin, Users } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })

const route = useRoute()
const { fetchRoom } = useRooms()

const room = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  room.value = await fetchRoom(route.params.id as string)
  loading.value = false
})
</script>

<template>
  <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
  <div v-else-if="room" class="max-w-4xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">{{ room.name }}</h1>
      <div class="flex items-center gap-4 mt-2 text-muted-foreground">
        <span class="flex items-center gap-1"><MapPin class="h-4 w-4" /> Этаж {{ room.floor }}</span>
        <span class="flex items-center gap-1"><Users class="h-4 w-4" /> до {{ room.capacity }} чел.</span>
      </div>
      <div class="flex gap-1 mt-3">
        <EquipmentBadge v-for="(val, key) in room.equipment" :key="key" v-show="val" :type="String(key)" />
      </div>
      <Badge v-if="room.requires_approval" variant="outline" class="mt-2">
        Требует подтверждения администратором
      </Badge>
    </div>

    <BookingForm :room-id="room.id" :room-name="room.name" />
  </div>
</template>
```

- [ ] **Step 5: Создать frontend/app/pages/bookings.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const { fetchMyBookings, cancelBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

const tab = ref<'upcoming' | 'past'>('upcoming')

const filtered = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  if (tab.value === 'upcoming') {
    return bookings.value.filter(b => b.date >= today && b.status !== 'cancelled' && b.status !== 'rejected')
  }
  return bookings.value.filter(b => b.date < today || b.status === 'cancelled' || b.status === 'rejected')
})

async function load() {
  loading.value = true
  bookings.value = await fetchMyBookings()
  loading.value = false
}

async function onCancel(id: string) {
  await cancelBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Мои брони</h1>

    <Tabs :default-value="tab" @update:model-value="(v) => tab = v as any" class="mb-6">
      <TabsList>
        <TabsTrigger value="upcoming">Предстоящие</TabsTrigger>
        <TabsTrigger value="past">Прошедшие</TabsTrigger>
      </TabsList>
    </Tabs>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else-if="filtered.length === 0" class="text-muted-foreground">Нет бронирований</div>
    <div v-else class="space-y-3">
      <BookingCard
        v-for="b in filtered"
        :key="b.id"
        :booking="b"
        :show-cancel="tab === 'upcoming'"
        @cancel="onCancel"
      />
    </div>
  </div>
</template>
```

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: страницы комнат, детали комнаты с бронированием, мои брони"
```

---

## Task 14: Фронтенд — страница менеджера

**Files:**
- Create: `frontend/app/pages/department.vue`

- [ ] **Step 1: Создать frontend/app/pages/department.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchDepartmentBookings } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  bookings.value = await fetchDepartmentBookings()
  loading.value = false
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Брони отдела</h1>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else-if="bookings.length === 0" class="text-muted-foreground">Нет бронирований</div>
    <div v-else class="space-y-3">
      <BookingCard v-for="b in bookings" :key="b.id" :booking="b" />
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "feat: страница менеджера — брони отдела"
```

---

## Task 15: Фронтенд — админ-страницы

**Files:**
- Create: `frontend/app/pages/admin/rooms.vue`
- Create: `frontend/app/pages/admin/bookings.vue`
- Create: `frontend/app/pages/admin/users.vue`
- Create: `frontend/app/pages/admin/settings.vue`

- [ ] **Step 1: Создать frontend/app/pages/admin/rooms.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchRooms, createRoom, updateRoom, deleteRoom } = useRooms()
const rooms = ref<any[]>([])
const showDialog = ref(false)
const editingRoom = ref<any>(null)
const form = ref({ name: '', floor: 1, capacity: 4, equipment: {}, requires_approval: false })
const loading = ref(true)

async function load() {
  loading.value = true
  rooms.value = await fetchRooms()
  loading.value = false
}

function openCreate() {
  editingRoom.value = null
  form.value = { name: '', floor: 1, capacity: 4, equipment: {}, requires_approval: false }
  showDialog.value = true
}

function openEdit(room: any) {
  editingRoom.value = room
  form.value = { ...room }
  showDialog.value = true
}

async function onSubmit() {
  if (editingRoom.value) {
    await updateRoom(editingRoom.value.id, form.value)
  } else {
    await createRoom(form.value)
  }
  showDialog.value = false
  await load()
}

async function onDelete(id: string) {
  await deleteRoom(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Управление комнатами</h1>
      <Button @click="openCreate">Добавить комнату</Button>
    </div>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead>Этаж</TableHead>
          <TableHead>Вместимость</TableHead>
          <TableHead>Подтверждение</TableHead>
          <TableHead>Действия</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="room in rooms" :key="room.id">
          <TableCell class="font-medium">{{ room.name }}</TableCell>
          <TableCell>{{ room.floor }}</TableCell>
          <TableCell>{{ room.capacity }}</TableCell>
          <TableCell>
            <Badge :variant="room.requires_approval ? 'default' : 'secondary'">
              {{ room.requires_approval ? 'Да' : 'Нет' }}
            </Badge>
          </TableCell>
          <TableCell>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="openEdit(room)">Изменить</Button>
              <Button variant="destructive" size="sm" @click="onDelete(room.id)">Удалить</Button>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <Dialog v-model:open="showDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ editingRoom ? 'Редактировать' : 'Создать' }} комнату</DialogTitle>
        </DialogHeader>
        <form @submit.prevent="onSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label>Название</Label>
            <Input v-model="form.name" required />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label>Этаж</Label>
              <Input v-model.number="form.floor" type="number" min="1" required />
            </div>
            <div class="space-y-2">
              <Label>Вместимость</Label>
              <Input v-model.number="form.capacity" type="number" min="1" required />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" id="approval" v-model="form.requires_approval" />
            <Label for="approval">Требует подтверждения</Label>
          </div>
          <Button type="submit" class="w-full">Сохранить</Button>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>
```

- [ ] **Step 2: Создать frontend/app/pages/admin/bookings.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchAllBookings, cancelBooking, approveBooking, rejectBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  bookings.value = await fetchAllBookings()
  loading.value = false
}

async function onCancel(id: string) {
  await cancelBooking(id)
  await load()
}

async function onApprove(id: string) {
  await approveBooking(id)
  await load()
}

async function onReject(id: string) {
  await rejectBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Все бронирования</h1>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else class="space-y-3">
      <div v-for="b in bookings" :key="b.id">
        <BookingCard
          :booking="b"
          show-cancel
          show-actions
          @cancel="onCancel"
          @approve="onApprove"
          @reject="onReject"
        />
        <p class="text-xs text-muted-foreground ml-4 mt-1">Автор: {{ b.user_name }}</p>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 3: Создать frontend/app/pages/admin/users.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })

const users = ref<any[]>([])
const departments = ref<any[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  const [u, d] = await Promise.all([
    $fetch<any[]>('/api/users'),
    $fetch<any[]>('/api/departments'),
  ])
  users.value = u
  departments.value = d
  loading.value = false
}

async function updateUser(userId: string, data: any) {
  await $fetch(`/api/users/${userId}`, { method: 'PATCH', body: data })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Пользователи</h1>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Имя</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Роль</TableHead>
          <TableHead>Статус</TableHead>
          <TableHead>Действия</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="user in users" :key="user.id">
          <TableCell class="font-medium">{{ user.name }}</TableCell>
          <TableCell>{{ user.email }}</TableCell>
          <TableCell>
            <Select
              :model-value="user.role"
              @update:model-value="(v) => updateUser(user.id, { role: v })"
            >
              <SelectTrigger class="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employee">Сотрудник</SelectItem>
                <SelectItem value="manager">Менеджер</SelectItem>
                <SelectItem value="admin">Админ</SelectItem>
              </SelectContent>
            </Select>
          </TableCell>
          <TableCell>
            <Badge :variant="user.is_active ? 'default' : 'destructive'">
              {{ user.is_active ? 'Активен' : 'Заблокирован' }}
            </Badge>
          </TableCell>
          <TableCell>
            <Button
              variant="outline" size="sm"
              @click="updateUser(user.id, { is_active: !user.is_active })"
            >
              {{ user.is_active ? 'Заблокировать' : 'Разблокировать' }}
            </Button>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
```

- [ ] **Step 4: Создать frontend/app/pages/admin/settings.vue**

```vue
<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'role'] })

const form = ref({
  max_duration_minutes: 120,
  max_days_ahead: 14,
  min_minutes_before_start: 15,
})
const loading = ref(true)
const saved = ref(false)

onMounted(async () => {
  const data = await $fetch<any>('/api/settings')
  form.value = data
  loading.value = false
})

async function onSubmit() {
  await $fetch('/api/settings', { method: 'PUT', body: form.value })
  saved.value = true
  setTimeout(() => (saved.value = false), 3000)
}
</script>

<template>
  <div class="max-w-lg">
    <h1 class="text-2xl font-bold mb-6">Настройки бронирования</h1>

    <Card>
      <CardContent class="pt-6">
        <form @submit.prevent="onSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label>Максимальная длительность (минуты)</Label>
            <Input v-model.number="form.max_duration_minutes" type="number" min="15" />
          </div>
          <div class="space-y-2">
            <Label>Горизонт бронирования (дней вперёд)</Label>
            <Input v-model.number="form.max_days_ahead" type="number" min="1" />
          </div>
          <div class="space-y-2">
            <Label>Минимум минут до начала встречи</Label>
            <Input v-model.number="form.min_minutes_before_start" type="number" min="0" />
          </div>
          <Button type="submit" class="w-full">Сохранить</Button>
          <p v-if="saved" class="text-sm text-green-600 text-center">Настройки сохранены</p>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: админ-страницы — комнаты, все брони, пользователи, настройки"
```

---

## Task 16: Финальная сборка и проверка

**Files:**
- Modify: `docker-compose.yml` (если нужны правки)

- [ ] **Step 1: Пересобрать и запустить**

```bash
docker compose down
docker compose up --build -d
```

- [ ] **Step 2: Применить миграции и сид**

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

- [ ] **Step 3: Проверить в браузере**

Открыть http://localhost:3000, проверить:
1. Регистрация и логин работают
2. Список переговорок отображается
3. Бронирование создаётся
4. Уведомления появляются
5. Админка доступна для admin@company.com
6. Менеджерская страница доступна для manager@company.com

- [ ] **Step 4: Финальный commit**

```bash
git add .
git commit -m "feat: финальная сборка и проверка системы бронирования"
```
