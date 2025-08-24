from repositories.user import PasswordService, UserRepository
from schemas.user import TokenDataSchema
from services.jwt import JWTService
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generators import get_random_string


class UserService:
    @staticmethod
    async def login(session: AsyncSession, email: str, password: str):
        user = await UserRepository.find(session=session, email=email)

        if not user or not user.is_active:
            return None

        if not PasswordService.verify(plain_pass=password, hashed_pass=user.password):
            return None

        access = JWTService.create_access(payload=user.to_payload)
        refresh = JWTService.create_refresh(payload=user.to_payload)

        return {"access": access, "refresh": refresh}

    @staticmethod
    async def register(session: AsyncSession, email: str, password: str):
        user = await UserRepository.create(session=session, email=email, password=password)
        return user

    @staticmethod
    async def send_key(session: AsyncSession, email: str):
        user = await UserRepository.find(session=session, email=email)

        if not user:
            return None

        key = get_random_string(72)
        user = await UserRepository.update(session=session, uuid=user.id, key=key)

        return user

    @staticmethod
    async def activate(session: AsyncSession, key: str):
        user = await UserRepository.find(session=session, key=key)

        if user and user.is_active:
            await UserRepository.update(session=session, uuid=user.id, key=None)
            return None

        elif not user:
            return None

        user = await UserRepository.update(session=session, uuid=user.id, is_active=True, key=None)

        return user

    @staticmethod
    async def change_password(session: AsyncSession, key: str, new_pass: str):
        user = await UserRepository.find(session=session, key=key)

        if not user:
            return None

        hashed_pass = PasswordService.hash(plain_pass=new_pass)
        user = await UserRepository.update(session=session, uuid=user.id, password=hashed_pass, key=None)

        return user

    @staticmethod
    async def delete(session: AsyncSession, user: TokenDataSchema):
        deleted = await UserRepository.delete(session=session, user_id=user.id)
        return deleted
