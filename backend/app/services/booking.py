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
