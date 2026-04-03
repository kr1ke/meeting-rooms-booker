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
