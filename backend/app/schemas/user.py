import uuid
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "employee"
    department_id: uuid.UUID | None = None


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
