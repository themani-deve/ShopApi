from uuid import UUID

from db.models import Product, ProductComment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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
        query = await session.execute(
            select(Product).options(selectinload(Product.owner), selectinload(Product.comments)).filter_by(**kwargs)
        )
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


class ProductCommentRepository:
    @staticmethod
    async def find(session: AsyncSession, **kwargs):
        query = await session.execute(
            select(ProductComment)
            .options(
                selectinload(ProductComment.user),
                selectinload(ProductComment.product),
                selectinload(ProductComment.parent),
            )
            .filter_by(**kwargs)
        )
        comment = query.scalar_one_or_none()

        return comment

    @staticmethod
    async def create(session: AsyncSession, user_id: UUID, product_id: UUID, text: str, parent_id: UUID = None):
        comment = ProductComment(text=text, user_id=user_id, product_id=product_id, parent_id=parent_id)
        session.add(comment)

        await session.commit()
        await session.refresh(comment, attribute_names=["user", "product", "parent"])

        return comment

    @staticmethod
    async def get_comments(session: AsyncSession, product_id: UUID, offset: int = 0, limit: int = 10):
        query = await session.execute(
            select(ProductComment)
            .options(
                selectinload(ProductComment.user),
                selectinload(ProductComment.product),
                selectinload(ProductComment.parent),
            )
            .filter_by(product_id=product_id)
            .offset(offset)
            .limit(limit)
        )
        comments = query.scalars().all()

        return comments
