from db.models import User
from services.pass_service import PasswordService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    @staticmethod
    async def create(session: AsyncSession, email: str, password: str):
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
    async def find(session: AsyncSession, **filters):
        query = select(User).filter_by(**filters)
        result = await session.execute(query)

        return result.scalars().first()
    
    @staticmethod
    async def update(session: AsyncSession, uuid: str, **kwargs):
        query = await session.execute(select(User).filter_by(id=uuid))
        user = query.scalars().first()

        if not user:
            return None
        
        for key, value in kwargs.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user
