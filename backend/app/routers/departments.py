from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.user import Department

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("")
async def list_departments(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Department).order_by(Department.name))
    departments = result.scalars().all()
    return [{"id": d.id, "name": d.name} for d in departments]
