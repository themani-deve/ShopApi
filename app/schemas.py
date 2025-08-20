from pydantic import BaseModel


class UserSchema(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access: str
    refresh: str


class SendActiveKeySchema(BaseModel):
    email: str
