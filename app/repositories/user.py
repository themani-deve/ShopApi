from uuid import UUID

from db.models import User
from services.password import PasswordService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    @staticmethod
    async def find(session: AsyncSession, **filters):
        query = select(User).filter_by(**filters)
        result = await session.execute(query)

        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, email: str, password: str):
        user = await UserRepository.find(session=session, email=email)

        if user:
            return None

        password = PasswordService.hash(plain_pass=password)

        user = User(email=email, password=password)
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def update(session: AsyncSession, uuid: UUID, **kwargs):
        user = await UserRepository.find(session=session, id=uuid)

        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def delete(session: AsyncSession, user_id: UUID):
        user = await UserRepository.find(session=session, id=user_id)

        if not user:
            return None

        await session.delete(user)
        await session.commit()

        return True
