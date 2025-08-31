import datetime
from typing import Optional

from core.settings import *
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generators import get_random_string
from utils.security import hashed_password, verify_password

from .exceptions import *
from .repositories import AccountRepository
from .schemas import *


class AccountService:
    INVALID_MSG = "Email or password is invalid!"
    CREATED_MSG = "User created successfully!"
    NOTFOUND_MSG = "User not found!"

    def __init__(self, db: AsyncSession):
        self.repo = AccountRepository(db=db)

    async def create_user(self, data: CreateUser) -> StringResponse:
        async with self.repo.db.begin():
            password_hashed = hashed_password(plain_pass=data.password)
            await self.repo.create(email=data.email, password_hashed=password_hashed)

            return StringResponse(detail=self.CREATED_MSG)

    async def login_user(self, data: LoginUser) -> Token:
        user = await self.repo.get(email=data.email)

        if not user or not verify_password(plain_pass=data.password, hashed_pass=user.password):
            raise InvalidCredentialsError(self.INVALID_MSG)

        elif not user.is_active:
            raise AccessDenied("Your account is not activated!")

        access_token = JWTService.create_access(payload=user.to_payload())
        refresh_token = JWTService.create_refresh(payload=user.to_payload())

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def send_key(self, data: SendKeyInput) -> StringResponse:
        async with self.repo.db.begin():
            user = await self.repo.get(email=data.email)
            if not user:
                raise UserNotFoundError(self.NOTFOUND_MSG)

            key = get_random_string(length=72)
            await self.repo.set_key(user=user, key=key)

            return StringResponse(detail="Code has been sent you!")

    async def activate_account(self, key: str) -> StringResponse:
        async with self.repo.db.begin():
            user = await self.repo.get(key=key)

            if not user:
                raise UserNotFoundError(self.NOTFOUND_MSG)

            elif user.is_active:
                await self.repo.deactivate_key(user=user)
                raise UserAlreadyActiveError("This account already been activated!")

            await self.repo.set_active(user=user)

            return StringResponse(detail="Your account has been activated!")

    async def change_password(self, key: str, data: ChangePassword) -> StringResponse:
        async with self.repo.db.begin():
            user = await self.repo.get(key=key)
            if not user:
                raise UserNotFoundError(self.NOTFOUND_MSG)

            password_hashed = hashed_password(plain_pass=data.password)
            await self.repo.change_password(user=user, password_hashed=password_hashed)

            return StringResponse(detail="Your password has been changed successfully!")

    async def delete_account(self, user: TokenData) -> StringResponse:
        async with self.repo.db.begin():
            user = await self.repo.get(id=user.id)
            if not user:
                raise UserNotFoundError(self.NOTFOUND_MSG)

            await self.repo.delete(user=user)

            return StringResponse(detail="Your account has been deleted successfully!")


class JWTService:
    @staticmethod
    def create_access(payload: dict) -> str:
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_EXPIRED_MINUTES)

        data = payload.copy()
        data.update({"exp": exp, "type": "access"})

        return jwt.encode(data, key=JWT_PRIVATE, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh(payload: dict) -> str:
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_EXPIRED_MINUTES)

        data = {"id": payload.get("id"), "exp": exp, "type": "refresh"}

        return jwt.encode(data, key=JWT_PRIVATE, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token=token, key=JWT_PUBLIC, algorithms=[JWT_ALGORITHM])

            token_type = payload.get("type")
            if token_type not in {"access", "refresh"}:
                raise InvalidTokenError("Invalid token type")

            return payload

        except ExpiredSignatureError:
            raise TokenExpiredError("Token expired")

        except JWTError:
            raise InvalidTokenError("Invalid token")
