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
