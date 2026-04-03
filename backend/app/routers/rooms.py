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
