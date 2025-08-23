from db.models import Cart, CartItem, Product, User
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
        query = await session.execute(select(Product).options(selectinload(Product.owner)).filter_by(**kwargs))
        product = query.scalar_one_or_none()

        return product


class CartRepository:
    @staticmethod
    async def find(session: AsyncSession, **kwargs):
        query = await session.execute(
            select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).filter_by(**kwargs)
        )
        cart = query.scalar_one_or_none()

        return cart

    @staticmethod
    async def create(session: AsyncSession, user: User):
        cart = await CartRepository.find(session=session, user_id=user.id, status=False)

        if not cart:
            cart = Cart(user=user)
            session.add(cart)

            await session.commit()
            await session.refresh(cart, attribute_names=["items"])

        return cart

    @staticmethod
    async def add_to_cart(session: AsyncSession, product: Product, cart: Cart, quantity: int):
        query = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
        )
        item = query.scalar_one_or_none()

        if not item:
            item = CartItem(cart=cart, product=product, quantity=quantity)
            session.add(item)
        else:
            item.quantity += quantity

        await session.commit()
        await session.refresh(cart, attribute_names=["items"])

        for item in cart.items:
            await session.refresh(item, attribute_names=["product"])

        return cart
