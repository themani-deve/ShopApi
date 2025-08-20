from pydantic import BaseModel


class LoginSchema(BaseModel):
    email: str
    password: str


class RegisterSchema(BaseModel):
    email: str
    password: str
    confirm_password: str

    @property
    def is_equal(self):
        if not self.password == self.confirm_password:
            return False
        return True


class TokenSchema(BaseModel):
    access: str
    refresh: str


class SendKeySchema(BaseModel):
    email: str


class ChangePasswordSchema(BaseModel):
    password: str
    confirm_password: str

    @property
    def is_equal(self):
        if not self.password == self.confirm_password:
            return False
        return True
