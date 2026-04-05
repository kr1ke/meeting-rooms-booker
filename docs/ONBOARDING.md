# Онбординг-гид по проекту BookRoom

## Обзор проекта

**BookRoom** — веб-приложение для бронирования переговорных комнат в офисе. Полнофункциональная система с фронтендом на Nuxt 3 и бэкендом на FastAPI, хранением данных в PostgreSQL 16, JWT-аутентификацией, ролевой моделью доступа и оркестрацией через Docker Compose.

### Языки и технологии

| Категория | Стек |
|-----------|------|
| Фронтенд | Vue, TypeScript, CSS |
| Бэкенд | Python |
| Инфраструктура | Dockerfile, YAML, JSON |
| Документация | Markdown |

### Фреймворки и библиотеки

- **Фронтенд:** Nuxt, Vue, Pinia, Tailwind CSS, shadcn-vue, Reka UI, VueUse
- **Бэкенд:** FastAPI, SQLAlchemy, Alembic, Pydantic
- **Инфраструктура:** Docker, Docker Compose

---

## Архитектурные слои

Проект организован в 9 архитектурных слоёв. Ниже описание каждого с ключевыми файлами.

### 1. Backend API

FastAPI-роутеры и определения эндпоинтов для авторизации, бронирований, комнат, пользователей, уведомлений, отделов и настроек. HTTP-интерфейс бэкенда BookRoom.

**Ключевые файлы:**
- `backend/app/routers/auth.py` — регистрация, вход, выход, получение текущего пользователя. JWT в httpOnly cookies.
- `backend/app/routers/bookings.py` — CRUD бронирований + approve/reject workflow. Ролевой контроль доступа для админских операций.
- `backend/app/routers/rooms.py` — список комнат с фильтрами (этаж/вместимость/оборудование), расписание, доступность по 30-минутным слотам, админский CRUD с мягким удалением.
- `backend/app/routers/users.py` — админское управление пользователями: список, создание, обновление.
- `backend/app/routers/notifications.py` — список уведомлений (лимит 50) и пометка прочитанными.
- `backend/app/routers/departments.py` — получение списка отделов.
- `backend/app/routers/settings.py` — GET/PUT настроек бронирования. Обновление только для админов.

### 2. Backend Services

Слой бизнес-логики: сервисы авторизации, бронирования и уведомлений, утилиты безопасности, dependency injection, точка входа приложения и сидирование базы.

**Ключевые файлы:**
- `backend/app/main.py` — точка входа FastAPI. Конфигурация CORS, подключение 7 роутеров, health-check `/api/health`.
- `backend/app/services/booking.py` — валидация бронирования: проверка комнаты, времени, ограничений по длительности и горизонту, детекция пересечений, автоматическое определение статуса.
- `backend/app/services/auth.py` — поиск пользователей по email, создание с хэшированным паролем, аутентификация.
- `backend/app/services/notification.py` — создание уведомлений в БД.
- `backend/app/security.py` — bcrypt-хэширование паролей и создание/декодирование JWT через python-jose.
- `backend/app/dependencies.py` — DI: сессия БД (`get_db`), извлечение пользователя из JWT (`get_current_user`), проверка ролей (`require_role`).
- `backend/app/seed.py` — заполнение БД тестовыми данными: отделы, пользователи (admin + сотрудники), комнаты, настройки.

### 3. Backend Data

ORM-модели SQLAlchemy, Pydantic-схемы для валидации запросов/ответов, подключение к БД, миграции Alembic.

**Ключевые файлы:**
- `backend/app/models/user.py` — модели User и Department. Роли: employee/manager/admin. Связи с бронированиями и уведомлениями.
- `backend/app/models/booking.py` — модель Booking. Статусы: pending/confirmed/rejected/cancelled. Связи с User, Room, Notification.
- `backend/app/models/room.py` — модель Room. JSONB-поле для оборудования, вместимость, этаж, флаг необходимости одобрения, soft-delete.
- `backend/app/models/notification.py` — модель Notification. Типы уведомлений по статусу бронирования.
- `backend/app/models/settings.py` — модель BookingSettings: макс. длительность, горизонт бронирования, минимальное время до начала.
- `backend/app/schemas/` — Pydantic-схемы для auth, booking, room, notification, settings, user.
- `backend/app/database.py` — async SQLAlchemy engine и session factory, генератор `get_db`.
- `backend/app/config.py` — pydantic-settings: database_url, secret_key, access_token_expire_minutes.
- `backend/alembic/versions/5b9217162f4f_initial_tables.py` — начальная миграция: 6 таблиц.

### 4. Frontend Pages & Layouts

Страницы Nuxt 3 для всех маршрутов и шаблоны лейаутов.

**Ключевые файлы:**
- `frontend/app/app.vue` — корневой компонент: NuxtLayout + NuxtPage.
- `frontend/app/pages/index.vue` — дашборд: таймлайн занятости комнат, навигация по датам, список ближайших бронирований, CTA быстрого бронирования.
- `frontend/app/pages/rooms/index.vue` — список комнат с фильтрами через RoomFilters и карточками RoomCard.
- `frontend/app/pages/rooms/[id].vue` — детальная страница комнаты с метаданными и формой бронирования BookingForm.
- `frontend/app/pages/bookings.vue` — бронирования пользователя с табами «предстоящие/прошедшие».
- `frontend/app/pages/login.vue` / `register.vue` — страницы авторизации на auth-лейауте.
- `frontend/app/pages/admin/` — админские страницы: bookings, rooms, settings, users.
- `frontend/app/layouts/default.vue` — основной лейаут: AppSidebar + AppHeader + контент.
- `frontend/app/layouts/auth.vue` — лейаут авторизации: сплит-панель с брендингом.

### 5. Frontend Feature Components

Доменные Vue-компоненты, организованные по функциональности.

**Ключевые файлы:**
- `frontend/app/components/booking/BookingCalendar.vue` — интерактивный таймлайн (08:00-20:00) с drag-выделением, touch-поддержкой, визуализацией бронирований.
- `frontend/app/components/booking/BookingForm.vue` — форма бронирования с визуальным выбором времени, пресетами длительности (30мин-2ч), ручным вводом.
- `frontend/app/components/booking/BookingCard.vue` — карточка бронирования со статус-бейджем, цветовым кодированием, кнопками действий.
- `frontend/app/components/layout/AppSidebar.vue` — боковая навигация с адаптивным мобильным режимом.
- `frontend/app/components/layout/AppHeader.vue` — шапка с хлебными крошками, датой, уведомлениями, профилем.
- `frontend/app/components/layout/NotificationBell.vue` — колокольчик с бейджем непрочитанных, авто-обновление каждые 30 сек.
- `frontend/app/components/layout/AuthPanel.vue` — декоративная панель для страниц авторизации.
- `frontend/app/components/room/RoomCard.vue` — строка комнаты в стиле Notion: название, этаж, вместимость, оборудование.
- `frontend/app/components/room/RoomFilters.vue` — фильтры по этажу и минимальной вместимости.
- `frontend/app/components/room/EquipmentBadge.vue` — бейдж оборудования с иконкой и цветом.

### 6. Frontend Service Layer

Composables, Pinia stores, middleware, API-прокси и утилиты.

**Ключевые файлы:**
- `frontend/app/composables/useAuth.ts` — самый часто используемый модуль (12 входящих связей). Login, register, logout, fetchSession.
- `frontend/app/composables/useBookings.ts` — CRUD бронирований: создание, отмена, подтверждение, отклонение.
- `frontend/app/composables/useRooms.ts` — API комнат: список, CRUD, доступность, расписание.
- `frontend/app/composables/useNotifications.ts` — загрузка уведомлений, делегация в store.
- `frontend/app/stores/auth.ts` — Pinia store: данные пользователя, isAuthenticated, isAdmin.
- `frontend/app/stores/notifications.ts` — Pinia store: уведомления, счётчик непрочитанных.
- `frontend/app/middleware/auth.ts` — guard: редирект неавторизованных на login.
- `frontend/app/middleware/role.ts` — guard: редирект не-админов с /admin страниц.
- `frontend/server/api/[...].ts` — catch-all прокси: все /api/* запросы переадресуются на бэкенд.
- `frontend/app/lib/utils.ts` — утилита `cn()` для мерджа Tailwind-классов.

### 7. Frontend UI Library

Компоненты shadcn-vue на основе Reka UI: AlertDialog, Avatar, Badge, Button, Card, Dialog, DropdownMenu, Input, Label, Select, Separator, Sheet, Table, Tabs, Toast. Это фундамент дизайн-системы BookRoom.

> Компоненты не устанавливаются из npm, а живут в кодовой базе (`frontend/app/components/ui/`) и полностью кастомизируемы.

### 8. Infrastructure & Configuration

Docker-файлы, конфигурации проекта и CSS-ассеты.

**Ключевые файлы:**
- `docker-compose.yml` — 3 сервиса: PostgreSQL 16 (порт 5434), FastAPI (порт 8000), Nuxt (порт 3000). Persistent volume для pgdata.
- `backend/Dockerfile` — python:3.12-slim, uvicorn с hot-reload.
- `frontend/Dockerfile` — node:20-alpine, nuxi dev server.
- `frontend/nuxt.config.ts` — модули Tailwind CSS, shadcn-nuxt, Pinia. SEO, Google Fonts, прокси бэкенда.
- `frontend/tailwind.config.ts` — тема с CSS-переменными shadcn-vue, плагин tailwindcss-animate.
- `frontend/app/assets/css/variables.css` — дизайн-токены: тёплая оранжевая тема, light/dark режимы, Plus Jakarta Sans.
- `backend/alembic.ini` — конфигурация Alembic.
- `backend/requirements.txt` — зависимости Python.
- `frontend/package.json` — зависимости npm.

### 9. Documentation

Документация проекта, спецификации и инструкции.

**Ключевые файлы:**
- `README.md` — обзор архитектуры, запуск через Docker Compose, тестовые аккаунты, функциональность.
- `CLAUDE.md` — инструкции для AI-агента: Docker для тестирования, комментарии на русском.
- `docs/superpowers/specs/2026-04-03-meeting-room-booking-design.md` — техническая спецификация: модели данных, REST API, роли, валидация.
- `docs/superpowers/plans/2026-04-03-meeting-room-booking.md` — план реализации из 16 задач.
- `.impeccable.md` — дизайн-контекст: целевая аудитория, палитра, шрифты, UI-библиотека.

---

## Ключевые концепции

### Ролевая модель доступа
Три роли: **employee**, **manager**, **admin**. Сотрудники бронируют комнаты и управляют своими бронями. Админы могут одобрять/отклонять бронирования, управлять комнатами, пользователями и настройками системы.

### JWT-аутентификация через httpOnly cookies
Токены хранятся в httpOnly cookies (не в localStorage), что повышает безопасность. Бэкенд устанавливает cookie при логине, фронтенд отправляет его автоматически.

### Dependency Injection (FastAPI)
Цепочка зависимостей: `get_db` (сессия БД) -> `get_current_user` (декодирование JWT) -> `require_role` (проверка роли). Каждый эндпоинт декларативно указывает свои требования через `Depends()`.

### Composable + Store (Vue 3 / Pinia)
Двухуровневый паттерн: composables (`use*`) инкапсулируют API-вызовы, Pinia stores хранят глобальное состояние. Это разделяет логику взаимодействия с API и управление состоянием.

### shadcn-vue: Copy-Paste компоненты
UI-компоненты не являются npm-зависимостью. Они скопированы в проект и полностью кастомизируемы. Построены на headless-примитивах Reka UI.

### Файловая маршрутизация Nuxt 3
Структура `pages/` автоматически определяет маршруты: `pages/rooms/[id].vue` -> `/rooms/:id`. Квадратные скобки обозначают динамические параметры.

### Валидация бронирований
Многоуровневая: проверка существования комнаты, время в будущем, ограничения длительности и горизонта из настроек, детекция пересечений с существующими бронями, автоопределение статуса (confirmed/pending) в зависимости от настроек комнаты.

### API-прокси
Фронтенд проксирует все `/api/*` запросы на бэкенд через catch-all серверный роут (`frontend/server/api/[...].ts`), что избавляет от CORS-проблем в продакшне.

---

## Путеводитель по коду

Пошаговый маршрут для изучения кодовой базы.

### Шаг 1. Обзор проекта
Начните с `README.md` — он описывает архитектуру (Nuxt 3 + FastAPI + PostgreSQL), запуск через Docker Compose, тестовые аккаунты и функциональность. `CLAUDE.md` содержит инструкции для AI-агента.

### Шаг 2. Инфраструктура и деплой
`docker-compose.yml` оркестрирует три сервиса: PostgreSQL 16 (порт 5434), FastAPI (порт 8000), Nuxt (порт 3000). `depends_on` задаёт порядок запуска: БД -> бэкенд -> фронтенд. Каждый `Dockerfile` определяет изолированный контекст сборки.

### Шаг 3. Точка входа бэкенда
`backend/app/main.py` — корень FastAPI-приложения. Создаёт экземпляр FastAPI, настраивает CORS, подключает 7 роутеров. Это хаб, соединяющий всю API-поверхность. Рядом `config.py` (настройки из .env) и `database.py` (async SQLAlchemy).

### Шаг 4. Модели данных
`backend/app/models/` — SQLAlchemy-модели: User (самая часто используемая, 10 входящих связей), Room, Booking, Notification, BookingSettings. Модуль `__init__.py` объявляет Base и импортирует все модели для Alembic.

### Шаг 5. API-слой бэкенда
Роутеры — узлы с наибольшим числом связей: `bookings.py` (13 связей) — CRUD + approve/reject, `rooms.py` (11 связей) — списки, расписания, слоты доступности. `auth.py` — JWT в httpOnly cookies.

### Шаг 6. Бизнес-логика и безопасность
`services/booking.py` — валидация временных ограничений, детекция пересечений, автоматический статус. `security.py` — bcrypt + JWT. `dependencies.py` — DI-цепочка: сессия -> пользователь -> роль.

### Шаг 7. Точка входа фронтенда
`frontend/app/app.vue` — корневой Vue-компонент с NuxtLayout/NuxtPage. `nuxt.config.ts` подключает Tailwind CSS, shadcn-nuxt, Pinia, настраивает SEO и прокси бэкенда. `tailwind.config.ts` расширяет тему дизайн-токенами.

### Шаг 8. Страницы и маршрутизация
`pages/index.vue` — дашборд с таймлайном. `pages/rooms/` — список и детали комнат. `pages/admin/` — админские страницы. `pages/login.vue` и `register.vue` — авторизация на отдельном лейауте.

### Шаг 9. Состояние и composables
`useAuth.ts` — самый часто используемый модуль (12 входящих связей). Composables делегируют состояние в Pinia stores. Middleware (`auth.ts`, `role.ts`) защищают маршруты.

### Шаг 10. Доменные компоненты
`BookingCalendar.vue` — самый сложный фронтенд-компонент: интерактивный таймлайн с drag-выделением и touch-поддержкой. `BookingForm.vue` интегрирует календарь с пресетами длительности. `AppSidebar.vue` — навигация с адаптивным мобильным режимом.

### Шаг 11. UI-библиотека (shadcn-vue)
Copy-paste примитивы на Reka UI: button, card, dialog, table, toast и др. Живут в `components/ui/`, полностью кастомизируемы. `components.json` — конфигурация генерации.

### Шаг 12. Миграции и документация
`alembic/versions/` — начальная миграция создаёт 6 таблиц. `seed.py` заполняет тестовыми данными. Дизайн-спецификация и план реализации в `docs/` прослеживают путь от требований до кода.

---

## Карта файлов

### Бэкенд: API-роутеры
| Файл | Назначение |
|------|-----------|
| `backend/app/routers/auth.py` | Регистрация, вход, выход, текущий пользователь (JWT cookies) |
| `backend/app/routers/bookings.py` | CRUD бронирований, одобрение/отклонение |
| `backend/app/routers/rooms.py` | Список, расписание, доступность, админский CRUD комнат |
| `backend/app/routers/users.py` | Админское управление пользователями |
| `backend/app/routers/notifications.py` | Список и пометка уведомлений |
| `backend/app/routers/departments.py` | Список отделов |
| `backend/app/routers/settings.py` | Чтение/обновление настроек бронирования |

### Бэкенд: Сервисы и логика
| Файл | Назначение |
|------|-----------|
| `backend/app/main.py` | Точка входа FastAPI, CORS, подключение роутеров |
| `backend/app/services/booking.py` | Валидация и создание бронирований |
| `backend/app/services/auth.py` | Аутентификация и создание пользователей |
| `backend/app/services/notification.py` | Создание уведомлений |
| `backend/app/security.py` | Хэширование паролей, JWT-токены |
| `backend/app/dependencies.py` | DI: сессия БД, текущий пользователь, проверка роли |
| `backend/app/seed.py` | Заполнение БД тестовыми данными |

### Бэкенд: Данные
| Файл | Назначение |
|------|-----------|
| `backend/app/models/user.py` | Модели User и Department |
| `backend/app/models/booking.py` | Модель Booking со статусами |
| `backend/app/models/room.py` | Модель Room с JSONB-оборудованием |
| `backend/app/models/notification.py` | Модель Notification |
| `backend/app/models/settings.py` | Модель BookingSettings |
| `backend/app/schemas/` | Pydantic-схемы для всех сущностей |
| `backend/app/database.py` | Async SQLAlchemy engine и сессии |
| `backend/app/config.py` | Настройки из переменных окружения |
| `backend/alembic/versions/` | Миграции базы данных |

### Фронтенд: Страницы
| Файл | Назначение |
|------|-----------|
| `frontend/app/pages/index.vue` | Дашборд с таймлайном занятости |
| `frontend/app/pages/rooms/index.vue` | Список комнат с фильтрами |
| `frontend/app/pages/rooms/[id].vue` | Детали комнаты и форма бронирования |
| `frontend/app/pages/bookings.vue` | Бронирования пользователя |
| `frontend/app/pages/login.vue` | Страница входа |
| `frontend/app/pages/register.vue` | Страница регистрации |
| `frontend/app/pages/admin/bookings.vue` | Админ: управление бронированиями |
| `frontend/app/pages/admin/rooms.vue` | Админ: управление комнатами |
| `frontend/app/pages/admin/users.vue` | Админ: управление пользователями |
| `frontend/app/pages/admin/settings.vue` | Админ: настройки системы |

### Фронтенд: Компоненты
| Файл | Назначение |
|------|-----------|
| `frontend/app/components/booking/BookingCalendar.vue` | Интерактивный таймлайн бронирования |
| `frontend/app/components/booking/BookingForm.vue` | Форма создания бронирования |
| `frontend/app/components/booking/BookingCard.vue` | Карточка бронирования |
| `frontend/app/components/layout/AppSidebar.vue` | Боковая навигация |
| `frontend/app/components/layout/AppHeader.vue` | Шапка с хлебными крошками |
| `frontend/app/components/layout/NotificationBell.vue` | Колокольчик уведомлений |
| `frontend/app/components/layout/AuthPanel.vue` | Декоративная панель авторизации |
| `frontend/app/components/room/RoomCard.vue` | Карточка комнаты |
| `frontend/app/components/room/RoomFilters.vue` | Фильтры комнат |
| `frontend/app/components/room/EquipmentBadge.vue` | Бейдж оборудования |

### Фронтенд: Сервисный слой
| Файл | Назначение |
|------|-----------|
| `frontend/app/composables/useAuth.ts` | Аутентификация (12 зависимостей) |
| `frontend/app/composables/useBookings.ts` | CRUD бронирований |
| `frontend/app/composables/useRooms.ts` | API комнат |
| `frontend/app/composables/useNotifications.ts` | Уведомления |
| `frontend/app/stores/auth.ts` | Pinia store авторизации |
| `frontend/app/stores/notifications.ts` | Pinia store уведомлений |
| `frontend/app/middleware/auth.ts` | Guard аутентификации |
| `frontend/app/middleware/role.ts` | Guard ролей |
| `frontend/server/api/[...].ts` | API-прокси на бэкенд |

### Инфраструктура
| Файл | Назначение |
|------|-----------|
| `docker-compose.yml` | Оркестрация: PostgreSQL + FastAPI + Nuxt |
| `backend/Dockerfile` | Сборка бэкенда (python:3.12-slim) |
| `frontend/Dockerfile` | Сборка фронтенда (node:20-alpine) |
| `frontend/nuxt.config.ts` | Конфигурация Nuxt: модули, SEO, прокси |
| `frontend/tailwind.config.ts` | Тема Tailwind с дизайн-токенами |
| `frontend/app/assets/css/variables.css` | CSS-переменные: тёплая оранжевая тема |

---

## Сложные участки кода

Следующие модули имеют повышенную сложность. При работе с ними рекомендуется проявлять особую внимательность.

### Бэкенд

| Файл | Причина сложности |
|------|-------------------|
| `backend/app/services/booking.py` | Многоуровневая валидация: проверка комнаты, время в будущем, ограничения длительности/горизонта из настроек, детекция пересечений, авто-статус. Функция `validate_and_create_booking` — центральная точка бизнес-логики. |
| `backend/app/routers/bookings.py` | 13 связей, самый «разветвлённый» роутер. CRUD + approve/reject + cancel с уведомлениями и ролевыми проверками. |
| `backend/app/routers/rooms.py` | 11 связей. Сложная логика генерации 30-минутных слотов доступности (08:00-20:00), расписание по дням, фильтрация. |
| `backend/alembic/versions/5b9217162f4f_initial_tables.py` | Начальная миграция с 6 таблицами, enum-типами, JSONB-полями и связями. |
| `backend/app/seed.py` | Асинхронная функция заполнения БД: отделы, 3 пользователя, 5 комнат с оборудованием, настройки. |

### Фронтенд

| Файл | Причина сложности |
|------|-------------------|
| `frontend/app/components/booking/BookingCalendar.vue` | Самый сложный фронтенд-компонент. Интерактивный таймлайн с click/drag выделением, touch-поддержкой, drag-resizable ручками, hover-превью, индикатором текущего времени. |
| `frontend/app/components/booking/BookingForm.vue` | Интеграция BookingCalendar + пресеты длительности + ручной ввод + загрузка доступности при смене даты. |
| `frontend/app/pages/index.vue` | Дашборд с таймлайном занятости, навигацией по датам и множественными источниками данных. |
| `frontend/app/pages/admin/users.vue` | Управление пользователями: таблица, редактирование ролей через select, диалоги блокировки/разблокировки, форма создания. |
| `frontend/app/components/ui/toast/use-toast.ts` | Reducer-style dispatch: add, update, dismiss, remove. Очередь авто-удаления, лимит тостов. |

### Документация

| Файл | Причина сложности |
|------|-------------------|
| `docs/superpowers/plans/2026-04-03-meeting-room-booking.md` | Комплексный план из 16 задач: от моделей до интеграции. |
| `docs/superpowers/specs/2026-04-03-meeting-room-booking-design.md` | Техническая спецификация: модели данных, API-эндпоинты, роли, валидация. |
