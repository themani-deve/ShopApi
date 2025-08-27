import re
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class TokenSchema(BaseModel):
    access: str
    refresh: str


class SendKeySchema(BaseModel):
    email: EmailStr


class ChangePasswordSchema(BaseModel):
    password: str
    confirm_password: str

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class TokenDataSchema(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_staff: bool


class UserSchema(BaseModel):
    email: str
    name: Optional[str]
    family: Optional[str]
    phone_number: Optional[str]

    class Config:
        from_attributes = True
