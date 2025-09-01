from datetime import datetime
from uuid import UUID

from core import settings
from product.models import Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .gateways import ZarinpalGateway
from .models import Cart, CartItem


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID) -> Cart:
        new_cart = Cart(user_id=user_id)

        self.db.add(new_cart)
        await self.db.flush()

        return new_cart

    async def get(self, **kwargs) -> Cart:
        query = await self.db.execute(
            select(Cart)
            .options(
                selectinload(Cart.user),
                selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.owner),
            )
            .filter_by(**kwargs)
        )

        return query.scalar_one_or_none()

    async def get_all(self, user_id: UUID) -> list[Cart]:
        query = await self.db.execute(
            select(Cart)
            .options(
                selectinload(Cart.items),
            )
            .where(Cart.user_id == user_id)
        )

        return query.scalars().all()

    async def update_amount(self, cart: Cart) -> Cart:
        cart.amount = sum(item.product.get_price * item.quantity for item in cart.items)
        return cart


class CartItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, cart: Cart, product: Product, quantity: int = 1) -> CartItem:
        item = await self.get(cart=cart, product=product)
        if not item:
            item = CartItem(quantity=quantity, cart=cart, product=product)

            self.db.add(item)
            await self.db.flush()
        else:
            item.quantity += quantity

        return item

    async def get(self, **kwargs) -> CartItem:
        query = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(CartItem.cart),
                selectinload(CartItem.product),
            )
            .filter_by(**kwargs)
        )

        return query.scalar_one_or_none()

    async def get_cart_items(self, **kwargs) -> list[CartItem]:
        query = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(CartItem.cart),
                selectinload(CartItem.product),
            )
            .filter_by(**kwargs)
        )

        return query.scalars().all()

    async def delete_cart_item(self, item: CartItem):
        await self.db.delete(item)


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def open_gate(self, cart: Cart):
        gateway = ZarinpalGateway(
            amount=cart.amount,
            description="Pay cart",
            callback_url=settings.ZARINPAL_CALLBACK_URL,
        )
        result = gateway.send_request

        if not result.get("success"):
            return result

        cart.authority = result.get("authority")

        return result

    async def verify_payment(self, cart: Cart):
        verify = ZarinpalGateway(amount=cart.amount).verify_payment(cart.authority)

        if not verify.get("success"):
            return verify

        cart.status = True
        cart.paid_at = datetime.utcnow()
        cart.ref_id = str(verify.get("ref_id"))

        return verify
