import re
from typing import Optional
from datetime import date, datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from src.app_users.shemas_user import UserResponse


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=120)
    last_name: str = Field(min_length=3, max_length=120)
    email_sec: EmailStr | None
    phone: Optional[str] = Field(
        None,
        min_length=3,
        max_length=15,
        description="Format +14445556677",
        json_schema_extra="+14445556677",
    )
    description: Optional[str] = Field(None, max_length=250)
    date_birth: Optional[date] = Field(None, description="Format YYYY-MM-DD")

    @field_validator("phone")
    def validate_phone(cls, value):
        if value:
            pattern = r"^\+?[1-9]\d{1,14}$"
            if not re.match(pattern, value):
                raise ValueError(f"Incorrect phone number {value}")
        return value


class ContactUpdateSchema(ContactSchema):
    pass


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email_sec: EmailStr | None
    phone: str | None
    description: str | None
    date_birth: date | None
    created_at: datetime | None
    user_id: uuid.UUID | None
    user: UserResponse | None
    model_config = ConfigDict(from_attributes=True)
