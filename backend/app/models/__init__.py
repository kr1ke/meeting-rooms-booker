from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Импорт всех моделей для Alembic
from app.models.user import User, Department  # noqa: E402, F401
from app.models.room import Room  # noqa: E402, F401
from app.models.booking import Booking  # noqa: E402, F401
from app.models.notification import Notification  # noqa: E402, F401
from app.models.settings import BookingSettings  # noqa: E402, F401
