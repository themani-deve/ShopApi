from db.models import Cart, CartItem, Product
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


class CartRepository:
    @staticmethod
    async def find_cart(session: AsyncSession, **kwargs):
        query = await session.execute(
            select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).filter_by(**kwargs)
        )
        result = query.scalar_one_or_none()

        return result

    @staticmethod
    async def find_item(session: AsyncSession, **kwargs):
        query = await session.execute(select(CartItem).options(selectinload(CartItem.product)).filter_by(**kwargs))
        result = query.scalar_one_or_none()

        return result

    @staticmethod
    async def create_cart(session: AsyncSession, user_id):
        cart = await CartRepository.find_cart(session=session, user_id=user_id, status=False)

        if not cart:
            cart = Cart(user_id=user_id)
            session.add(cart)

            await session.commit()
            await session.refresh(cart)

        return cart

    @staticmethod
    async def add(session: AsyncSession, cart_id: UUID, product_id: UUID, quantity: int):
        item = await CartRepository.find_item(session=session, cart_id=cart_id, product_id=product_id)

        if not item:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            session.add(item)

        else:
            item.quantity += quantity

        await session.commit()
        await session.refresh(item)

        return item
