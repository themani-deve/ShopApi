from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class StringResponse(BaseModel):
    detail: str


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class SendKeyInput(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    password: str
    confirm_password: str


class TokenData(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_staff: bool
