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
