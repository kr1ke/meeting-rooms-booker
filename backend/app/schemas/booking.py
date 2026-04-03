import uuid
from datetime import date, time, datetime
from pydantic import BaseModel


class BookingCreate(BaseModel):
    room_id: uuid.UUID
    title: str
    date: date
    start_time: time
    end_time: time


class BookingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    room_id: uuid.UUID
    title: str
    date: date
    start_time: time
    end_time: time
    status: str
    created_at: datetime
    user_name: str | None = None
    room_name: str | None = None

    model_config = {"from_attributes": True}
