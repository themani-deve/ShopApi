from uuid import UUID

from repositories.cart import CartRepository
from repositories.product import ProductRepository
from repositories.user import UserRepository
from schemas.user import TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession


class CartService:
    @staticmethod
    async def add(session: AsyncSession, user: TokenDataSchema, product_id: UUID, quantity: int):
        user = await UserRepository.find(session=session, id=user.id, is_active=True)
        if not user:
            return None

        product = await ProductRepository.find(session=session, id=product_id, is_active=True)
        if not product:
            return None

        cart = await CartRepository.create_cart(session=session, user_id=user.id)
        if not cart:
            return None

        item = await CartRepository.add(session=session, cart_id=cart.id, product_id=product.id, quantity=quantity)

        return item

    @staticmethod
    async def get_cart_items(session: AsyncSession, user: TokenDataSchema):
        user = await UserRepository.find(session=session, id=user.id, is_active=True)
        if not user:
            return None

        cart = await CartRepository.find_cart(session=session, user_id=user.id, status=False)
        if not cart:
            cart = await CartRepository.create_cart(session=session, user_id=user.id)

        return cart
