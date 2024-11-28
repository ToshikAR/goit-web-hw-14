from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    last_visit: datetime
    created_at: datetime
    avatar: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)
