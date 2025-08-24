from db.models import Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID


class ProductRepository:
    @staticmethod
    async def create(session: AsyncSession, data: dict):
        product = Product(**data)
        session.add(product)

        await session.commit()
        await session.refresh(product, attribute_names=["owner"])

        return product

    @staticmethod
    async def get_all(session: AsyncSession):
        query = await session.execute(select(Product).options(selectinload(Product.owner)).filter_by(is_active=True))
        products = query.scalars().all()

        return products

    @staticmethod
    async def find(session: AsyncSession, **kwargs):
        query = await session.execute(select(Product).options(selectinload(Product.owner)).filter_by(**kwargs))
        product = query.scalar_one_or_none()

        return product
    
    @staticmethod
    async def delete(session: AsyncSession, product_id: UUID):
        product = await ProductRepository.find(session=session, id=product_id)

        if not product:
            return None
        
        await session.delete(product)
        await session.commit()

        return True
