from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .exceptions import UserAlreadyExistsError
from .models import User


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, email: str, password_hashed: str) -> User:
        """Create a new user."""
        if await self.get(email=email):
            raise UserAlreadyExistsError("User with this email already exists!")

        user = User(email=email, password=password_hashed)

        self.db.add(user)
        await self.db.flush()

        return user

    async def get(self, with_related: bool = False, **kwargs) -> Optional[User]:
        """Find user record in database."""
        stmt = select(User).filter_by(**kwargs)

        if with_related:
            stmt = stmt.options(
                selectinload(User.products),
                selectinload(User.comments),
                selectinload(User.carts),
            )

        query = await self.db.execute(stmt)

        return query.scalar_one_or_none()

    async def save_changes(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)

        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)

    async def set_key(self, user: User, key: str) -> User:
        """Set key for user."""
        return await self.save_changes(user=user, key=key)

    async def deactivate_key(self, user: User) -> User:
        """Clear user key."""
        return await self.save_changes(user=user, key=None)

    async def set_active(self, user: User) -> User:
        """Mark user as active and clear key."""
        return await self.save_changes(user=user, key=None, is_active=True)

    async def change_password(self, user: User, password_hashed: str) -> User:
        """Change user password."""
        return await self.save_changes(user=user, key=None, password=password_hashed)
