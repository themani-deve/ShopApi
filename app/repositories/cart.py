from datetime import datetime
from uuid import UUID

from core import settings
from db.models import Cart, CartItem, Product
from services.gateways import ZarinpalGateway
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CartRepository:
    @staticmethod
    async def find_cart(session: AsyncSession, **kwargs):
        query = await session.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.owner))
            .filter_by(**kwargs)
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
            await session.refresh(cart, attribute_names=["items"])

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

    @staticmethod
    async def delete_item(session: AsyncSession, item_id: UUID):
        item = await CartRepository.find_item(session=session, id=item_id)

        if not item:
            return None

        await session.delete(item)
        await session.commit()

        return True

    @staticmethod
    async def get_history(session: AsyncSession, user_id):
        query = await session.execute(select(Cart).filter_by(user_id=user_id))
        carts = query.scalars().all()

        return carts

    @staticmethod
    async def update_cart_amount(session: AsyncSession, cart: Cart):
        await session.refresh(cart, attribute_names=["items"])
        
        cart.amount = sum(item.product.get_price * item.quantity for item in cart.items)
        await session.commit()


class CartPaymentRepository:
    @staticmethod
    async def open_gate(session: AsyncSession, cart: Cart):
        gateway = ZarinpalGateway(
            amount=cart.amount,
            description="Pay cart",
            callback_url=settings.ZARINPAL_CALLBACK_URL,
        )
        result = gateway.send_request

        if not result.get("success"):
            return result

        cart.authority = result.get("authority")

        await session.commit()
        await session.refresh(cart, attribute_names=["items"])

        return result

    @staticmethod
    async def verify_payment(session: AsyncSession, cart: Cart):
        verify = ZarinpalGateway(amount=cart.amount).verify_payment(cart.authority)

        if not verify.get("success"):
            return verify

        cart.status = True
        cart.paid_at = datetime.utcnow()
        cart.ref_id = str(verify.get("ref_id"))

        await session.commit()
        await session.refresh(cart, attribute_names=["items"])

        return verify
