import uuid
from pydantic import BaseModel


class UserUpdate(BaseModel):
    role: str | None = None
    department_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserListResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    department_id: uuid.UUID | None
    is_active: bool

    model_config = {"from_attributes": True}
