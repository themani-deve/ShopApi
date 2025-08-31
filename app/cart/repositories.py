from uuid import UUID

from product.models import Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    async def update_amount(self, cart_id: UUID) -> Cart:
        cart = await self.get(id=cart_id)
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
