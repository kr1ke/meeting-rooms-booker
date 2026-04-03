import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    message: str
    is_read: bool
    booking_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
