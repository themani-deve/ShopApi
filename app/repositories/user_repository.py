from db.models import User
from services.pass_service import PasswordService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    @staticmethod
    async def create_user(session: AsyncSession, email: str, password: str):
        query = await session.execute(select(User).filter_by(email=email))
        user = query.scalars().first()

        if user:
            return None

        password = PasswordService.hash(plain_pass=password)

        user = User(email=email, password=password)
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def find_user(session: AsyncSession, **filters):
        query = select(User).filter_by(**filters)
        result = await session.execute(query)

        return result.scalars().first()
