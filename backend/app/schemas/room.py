import uuid
from datetime import time
from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    floor: int
    capacity: int
    equipment: dict = {}
    requires_approval: bool = False


class RoomUpdate(BaseModel):
    name: str | None = None
    floor: int | None = None
    capacity: int | None = None
    equipment: dict | None = None
    requires_approval: bool | None = None
    is_active: bool | None = None


class RoomResponse(BaseModel):
    id: uuid.UUID
    name: str
    floor: int
    capacity: int
    equipment: dict
    requires_approval: bool
    is_active: bool

    model_config = {"from_attributes": True}


class AvailabilitySlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool
    booking_title: str | None = None
