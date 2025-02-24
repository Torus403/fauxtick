import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    is_active: bool
    is_superuser: bool
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserUpdateMe(BaseModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=255)
    last_name: Optional[str] = Field(default=None, max_length=255)


class Message(BaseModel):
    message: str


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    first_name: Optional[str] = Field(default=None, max_length=255)
    last_name: Optional[str] = Field(default=None, max_length=255)


class UsersPublic(BaseModel):
    data: List[UserPublic]
    count: int
