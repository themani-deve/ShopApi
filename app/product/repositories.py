from account.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Product


class ProductRepository:
    def __init__(self, db: AsyncSession) -> Product:
        self.db = db

    async def create(self, name: str, price: int, discount: int, count: int, is_active: bool, slug: str, owner: User):
        new_product = Product(name=name, price=price, discount=discount, count=count, is_active=is_active, slug=slug)
        new_product.owner = owner

        self.db.add(new_product)
        await self.db.flush()

        return new_product

    async def get(self, **kwargs) -> Product:
        query = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.owner),
                selectinload(Product.comments),
            )
            .filter_by(**kwargs)
        )

        return query.scalar_one_or_none()

    async def get_all(self) -> list[Product]:
        query = await self.db.execute(
            select(Product).options(
                selectinload(Product.owner),
                selectinload(Product.comments),
            )
        )

        return query.scalars().all()

    async def delete(self, product: Product):
        await self.db.delete(product)
