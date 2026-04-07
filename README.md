> ## 🚀 [Мой сетап → SETUP.md](./SETUP.md)
>
> **Главное в этом репо.** Полный список инструментов, плагинов и MCP, которые я использую в Claude Code. С готовыми командами установки.

---

# BookRoom — Система бронирования переговорных

Веб-приложение для бронирования переговорных комнат в офисе. Сотрудники выбирают комнату, время и создают бронь. Администраторы управляют комнатами, пользователями и настройками.

## Быстрый старт

```bash
# Клонировать и запустить
git clone <repo-url> && cd bookroom
docker compose up --build
```

Приложение будет доступно:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs

### Тестовые аккаунты

| Email | Пароль | Роль |
|---|---|---|
| admin@company.com | admin123 | Администратор |
| user@company.com | user123 | Сотрудник |
| manager@company.com | manager123 | Сотрудник |

При первом запуске автоматически создаются тестовые данные: пользователи, отделы и комнаты.

## Возможности

### Для сотрудников
- **Дашборд** — таймлайн загруженности всех комнат на сегодня, ближайшие брони
- **Переговорки** — каталог комнат с фильтрами по этажу и вместимости
- **Бронирование** — визуальный выбор времени на таймлайне с drag-resize, ручной ввод до минуты
- **Мои брони** — список предстоящих и прошедших бронирований, отмена

### Для администраторов
- **Управление комнатами** — создание, редактирование, удаление переговорок
- **Все бронирования** — просмотр и отмена броней всех сотрудников
- **Пользователи** — создание аккаунтов, смена ролей, блокировка
- **Настройки** — лимит длительности, горизонт бронирования, минимальное время до начала

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Nuxt 3    │────▶│   FastAPI    │────▶│ PostgreSQL   │
│  (Vue 3)    │     │  (async)    │     │   16         │
│  port 3000  │     │  port 8000  │     │  port 5434   │
└─────────────┘     └─────────────┘     └──────────────┘
```

### Frontend (`frontend/`)
- **Nuxt 3** + **Vue 3** (Composition API, `<script setup>`)
- **Tailwind CSS** + **shadcn-vue** (reka-ui) — UI-компоненты
- **Pinia** — стор авторизации
- Шрифт: Plus Jakarta Sans, тёплая палитра (оранжевый акцент)

Структура:
```
frontend/app/
├── pages/           # Страницы (file-based routing)
│   ├── index.vue         # Дашборд
│   ├── rooms/            # Каталог и детали комнат
│   ├── bookings.vue      # Мои брони
│   ├── admin/            # Админ-панель
│   ├── login.vue
│   └── register.vue
├── components/      # Компоненты
│   ├── booking/          # BookingCalendar, BookingForm, BookingCard
│   ├── room/             # RoomCard, RoomFilters, EquipmentBadge
│   ├── layout/           # AppSidebar, AppHeader, NotificationBell
│   └── ui/               # AlertDialog (shadcn-vue)
├── composables/     # useBookings, useRooms, useAuth
├── stores/          # Pinia (auth.ts)
├── layouts/         # default (sidebar), auth (login/register)
└── middleware/      # auth, role
```

### Backend (`backend/`)
- **FastAPI** + **SQLAlchemy 2.0** (async) + **Alembic** (миграции)
- JWT-аутентификация (access token)
- Валидация через Pydantic v2

Структура:
```
backend/app/
├── main.py          # FastAPI app, подключение роутеров
├── models/          # SQLAlchemy модели (User, Room, Booking, etc.)
├── schemas/         # Pydantic-схемы запросов/ответов
├── routers/         # API-эндпоинты
│   ├── auth.py           # POST /api/auth/login, /register
│   ├── rooms.py          # CRUD комнат + расписание
│   ├── bookings.py       # CRUD бронирований
│   ├── users.py          # Управление пользователями (admin)
│   ├── departments.py    # Список отделов
│   ├── notifications.py  # Уведомления
│   └── settings.py       # Настройки бронирования
├── services/        # Бизнес-логика (auth)
├── dependencies.py  # DI (get_db, require_role)
└── security.py      # JWT, хеширование паролей
```

### Инфраструктура
- **Docker Compose** — три сервиса: `db`, `backend`, `frontend`
- Volumes: `pgdata` для данных PostgreSQL, bind-mount для hot reload
- Seed-данные загружаются при первом запуске (`backend/app/seed.py`)
