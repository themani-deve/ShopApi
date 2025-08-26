from repositories.user import PasswordService, UserRepository
from schemas.response import ServiceResult
from schemas.user import TokenDataSchema, TokenSchema
from services.jwt import JWTService
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generators import get_random_string


class UserService:
    @staticmethod
    async def login(session: AsyncSession, email: str, password: str) -> ServiceResult:
        user = await UserRepository.find(session=session, email=email)

        if not user:
            return ServiceResult(success=False, message="Email or password not correct", status_code=400)

        if not PasswordService.verify(plain_pass=password, hashed_pass=user.password):
            return ServiceResult(success=False, message="Email or password not correct", status_code=400)

        if not user.is_active:
            return ServiceResult(success=False, message="Account not activated", status_code=403)

        response = TokenSchema(
            access=JWTService.create_access(payload=user.to_payload),
            refresh=JWTService.create_refresh(payload=user.to_payload),
        )

        return ServiceResult(success=True, data=response)

    @staticmethod
    async def register(session: AsyncSession, email: str, password: str) -> ServiceResult:
        user = await UserRepository.create(session=session, email=email, password=password)
        if not user:
            return ServiceResult(success=False, message="Email already exists", status_code=400)

        return ServiceResult(success=True, message="User created successfully")

    @staticmethod
    async def send_key(session: AsyncSession, email: str) -> ServiceResult:
        user = await UserRepository.find(session=session, email=email)
        if not user:
            return ServiceResult(success=False, message="User not found", status_code=404)

        await UserRepository.update(session=session, uuid=user.id, key=get_random_string(72))

        return ServiceResult(success=True, message="Key has been sent you")

    @staticmethod
    async def change_password(session: AsyncSession, key: str, new_pass: str) -> ServiceResult:
        user = await UserRepository.find(session=session, key=key)
        if not user:
            return ServiceResult(success=False, message="Key is invalid", status_code=404)

        await UserRepository.update(
            session=session, uuid=user.id, password=PasswordService.hash(plain_pass=new_pass), key=None
        )

        return ServiceResult(success=True, message="Your password has changed successfuly")

    @staticmethod
    async def activate(session: AsyncSession, key: str) -> ServiceResult:
        user = await UserRepository.find(session=session, key=key)

        if not user:
            return ServiceResult(success=False, message="Key is invalid", status_code=404)

        if user.is_active:
            await UserRepository.update(session=session, uuid=user.id, key=None)
            return ServiceResult(success=False, message="Account is activated", status_code=400)

        await UserRepository.update(session=session, uuid=user.id, is_active=True, key=None)

        return ServiceResult(success=True, message="Your account has been activated")

    @staticmethod
    async def delete(session: AsyncSession, user: TokenDataSchema) -> ServiceResult:
        user = await UserRepository.delete(session=session, user_id=user.id)
        if not user:
            return ServiceResult(success=False, message="User not found", status_code=404)

        return ServiceResult(success=True, message="Account deleted successfuly")
