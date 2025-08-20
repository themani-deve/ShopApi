from repositories.jwt_repository import JWTManager
from repositories.user_repository import PasswordService, UserRepository
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

        access = JWTManager.create_access(payload=user.to_payload)
        refresh = JWTManager.create_refresh(payload=user.to_payload)

        return {"access": access, "refresh": refresh}

    @staticmethod
    async def register(session: AsyncSession, email: str, password: str):
        user = await UserRepository.create(session=session, email=email, password=password)
        return user

    @staticmethod
    async def send_key(session: AsyncSession, email: str):
        user = await UserRepository.find(session=session, email=email, is_active=False)

        if not user:
            return None

        active_key = get_random_string(72)
        user = await UserRepository.update(session=session, uuid=user.id, active_key=active_key)

        return user

    @staticmethod
    async def activate(session: AsyncSession, active_key: str):
        user = await UserRepository.find(session=session, active_key=active_key, is_active=False)

        if not user:
            return None

        user = await UserRepository.update(session=session, uuid=user.id, is_active=True, active_key=None)

        return user
