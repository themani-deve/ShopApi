from repositories.jwt_repository import JWTManager
from repositories.user_repository import PasswordService, UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @staticmethod
    async def login(session: AsyncSession, email: str, password: str):
        user = await UserRepository.find_user(session=session, email=email)

        if not user:
            return None

        if not PasswordService.verify(plain_pass=password, hashed_pass=user.password):
            return None

        access = JWTManager.create_access(payload=user.to_payload)
        refresh = JWTManager.create_refresh(payload=user.to_payload)

        return {"access": access, "refresh": refresh}

    @staticmethod
    async def register(session: AsyncSession, email: str, password: str):
        user = await UserRepository.create_user(session=session, email=email, password=password)

        if not user:
            return None

        return user
