from pydantic import BaseModel


class SettingsResponse(BaseModel):
    max_duration_minutes: int
    max_days_ahead: int
    min_minutes_before_start: int

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    max_duration_minutes: int | None = None
    max_days_ahead: int | None = None
    min_minutes_before_start: int | None = None
