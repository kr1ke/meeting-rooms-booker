# Система бронирования переговорок

## Обзор

Веб-приложение для бронирования переговорных комнат в одном здании. Три роли пользователей, бронирование с ограничениями и механизмом подтверждения для отдельных комнат.

**Стек:** Nuxt 4 + Tailwind + shadcn-vue (фронтенд), FastAPI + PostgreSQL (бэкенд), Docker Compose (деплой).
**Акцентный цвет:** синий.

## Роли

- **Сотрудник** — бронирует переговорки, управляет своими бронями
- **Менеджер отдела** — видит все брони сотрудников своего отдела
- **Администратор** — управляет комнатами, пользователями, подтверждает/отклоняет заявки, отменяет чужие брони, настраивает глобальные правила

## Авторизация

Email + пароль. JWT токен хранится в httpOnly cookie через Nuxt server routes.

## Страницы

### Публичные
- `/login` — вход (email + пароль)
- `/register` — регистрация (имя, email, пароль, отдел)

### Сотрудник
- `/` — дашборд: ближайшие брони, быстрый поиск свободной переговорки, уведомления
- `/rooms` — список комнат с фильтрами (этаж, вместимость, оборудование), карточки с доступностью
- `/rooms/:id` — детали комнаты, календарь доступности, форма бронирования
- `/bookings` — мои бронирования (предстоящие/прошедшие), отмена

### Менеджер отдела
- `/department` — все бронирования сотрудников своего отдела

### Администратор
- `/admin/rooms` — CRUD переговорок, настройка оборудования, флаг «требует подтверждения»
- `/admin/bookings` — все брони, подтверждение/отклонение заявок, отмена
- `/admin/users` — управление пользователями: смена ролей, привязка к отделу, блокировка
- `/admin/settings` — глобальные правила бронирования

## Модель данных

### users
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| email | VARCHAR(255) | Уникальный |
| password_hash | VARCHAR(255) | Хеш пароля |
| name | VARCHAR(255) | Имя сотрудника |
| role | ENUM | employee / manager / admin |
| department_id | UUID FK | Отдел |
| is_active | BOOLEAN | Активен ли аккаунт |
| created_at | TIMESTAMP | Дата создания |

### departments
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| name | VARCHAR(255) | Название отдела |
| created_at | TIMESTAMP | Дата создания |

### rooms
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| name | VARCHAR(100) | Название комнаты |
| floor | INTEGER | Этаж |
| capacity | INTEGER | Вместимость |
| equipment | JSONB | Оборудование: проектор, доска, видеоконференция |
| requires_approval | BOOLEAN | Требует подтверждения админом |
| is_active | BOOLEAN | Активна ли комната |
| created_at | TIMESTAMP | Дата создания |

### bookings
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| user_id | UUID FK | Кто забронировал |
| room_id | UUID FK | Какая комната |
| title | VARCHAR(255) | Название встречи |
| date | DATE | Дата бронирования |
| start_time | TIME | Начало |
| end_time | TIME | Конец |
| status | ENUM | pending / confirmed / rejected / cancelled |
| created_at | TIMESTAMP | Дата создания |

### booking_settings
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| max_duration_minutes | INTEGER | Макс. длительность брони |
| max_days_ahead | INTEGER | На сколько дней вперёд можно бронировать |
| min_minutes_before_start | INTEGER | Минимум минут до начала встречи |

### notifications
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | PK |
| user_id | UUID FK | Кому |
| booking_id | UUID FK | Связанная бронь |
| type | ENUM | booking_confirmed / booking_rejected / booking_cancelled |
| message | TEXT | Текст уведомления |
| is_read | BOOLEAN | Прочитано |
| created_at | TIMESTAMP | Дата создания |

### Связи
- user → department (many-to-one)
- booking → user (many-to-one)
- booking → room (many-to-one)
- notification → user (many-to-one)
- notification → booking (many-to-one)

### Логика статусов бронирования
- Комната без `requires_approval` → бронь сразу `confirmed`
- Комната с `requires_approval` → бронь создаётся как `pending`, админ подтверждает (`confirmed`) или отклоняет (`rejected`)
- Отмена пользователем → `cancelled`

## API

### Auth
| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Логин, устанавливает JWT cookie |
| GET | /api/auth/me | Текущий пользователь |

### Rooms
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/rooms | Список комнат (фильтры: этаж, вместимость, оборудование) |
| GET | /api/rooms/:id | Детали комнаты |
| GET | /api/rooms/:id/availability?date= | Слоты доступности на дату |
| POST | /api/rooms | Создать комнату (admin) |
| PUT | /api/rooms/:id | Редактировать (admin) |
| DELETE | /api/rooms/:id | Удалить (admin) |

### Bookings
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/bookings | Мои брони |
| GET | /api/bookings/department | Брони отдела (manager) |
| GET | /api/bookings/all | Все брони (admin) |
| POST | /api/bookings | Создать бронь |
| PATCH | /api/bookings/:id/cancel | Отменить |
| PATCH | /api/bookings/:id/approve | Подтвердить (admin) |
| PATCH | /api/bookings/:id/reject | Отклонить (admin) |

### Users (admin)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/users | Список пользователей |
| PATCH | /api/users/:id | Изменить роль/отдел/статус |

### Departments
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/departments | Список отделов |

### Notifications
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/notifications | Уведомления текущего пользователя |
| PATCH | /api/notifications/:id/read | Пометить как прочитанное |

### Settings
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/settings | Настройки бронирования |
| PUT | /api/settings | Обновить (admin) |

## Архитектура

### Подход — монорепо с единым деплоем

```
vibecode-test/
├── docker-compose.yml
├── frontend/
│   ├── nuxt.config.ts
│   ├── app/
│   │   ├── layouts/            # default (сайдбар), auth (логин/регистрация)
│   │   ├── pages/              # Все страницы
│   │   ├── components/
│   │   │   ├── ui/             # shadcn компоненты
│   │   │   ├── booking/        # BookingForm, BookingCard, Calendar
│   │   │   ├── room/           # RoomCard, RoomFilters, EquipmentBadge
│   │   │   └── layout/         # Sidebar, Header, NotificationBell
│   │   ├── composables/        # useAuth, useBookings, useRooms, useNotifications
│   │   ├── middleware/         # auth.ts, role.ts
│   │   └── stores/             # Pinia: auth, bookings, rooms, notifications
│   ├── server/
│   │   └── api/[...].ts        # Прокси к FastAPI
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/             # SQLAlchemy модели
│   │   ├── schemas/            # Pydantic схемы
│   │   ├── routers/            # auth, rooms, bookings, users, notifications, settings
│   │   ├── services/           # Бизнес-логика
│   │   ├── dependencies.py     # get_db, get_current_user
│   │   └── security.py         # JWT, хеширование паролей
│   ├── alembic/                # Миграции
│   ├── requirements.txt
│   └── Dockerfile
└── .env
```

### Ключевые решения
- **JWT** в httpOnly cookie через Nuxt server routes — безопасно, не доступен из JS
- **Alembic** для миграций БД
- **Pinia** для state management
- **shadcn-vue** с синим акцентным цветом
- **Nuxt server proxy** — фронт не обращается к FastAPI напрямую, всё через Nuxt `/api/`
- **Docker Compose** — Nuxt (порт 3000), FastAPI (порт 8000, внутренний), PostgreSQL (порт 5432)

### Валидация бронирования (бэкенд)
1. Проверка что комната существует и активна
2. Проверка что время в будущем
3. Проверка ограничений из booking_settings (длительность, горизонт, мин. время до начала)
4. Проверка отсутствия пересечений с другими подтверждёнными/ожидающими бронями
5. Если комната requires_approval → статус `pending`, иначе `confirmed`
6. Создание уведомления пользователю
