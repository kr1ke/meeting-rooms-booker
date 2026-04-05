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
        # Обычный сотрудник вместо менеджера
        manager = User(
            email="maria@company.com",
            password_hash=hash_password("user456"),
            name="Мария Иванова",
            role=UserRole.employee,
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
