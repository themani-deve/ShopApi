from uuid import UUID

from account.schemas import StringResponse, TokenData
from product.exception import ProductNotFoundError
from product.repositories import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import *
from .repositories import CartItemRepository, CartRepository, PaymentRepository
from .schemas import AddCartItem, CartData, CartDetail, CartItemData


class CartService:
    def __init__(self, db: AsyncSession):
        self.cart_repo = CartRepository(db=db)
        self.cart_item_repo = CartItemRepository(db=db)
        self.product_repo = ProductRepository(db=db)

    async def add(self, user: TokenData, product_id: UUID, data: AddCartItem) -> StringResponse | Exception:
        async with self.cart_repo.db.begin():
            cart = await self.cart_repo.get(user_id=user.id, status=False)
            if not cart:
                cart = await self.cart_repo.create(user_id=user.id)

            product = await self.product_repo.get(id=product_id)
            if not product:
                raise ProductNotFoundError(f"Product with id `{product_id}` not found!")

            await self.cart_item_repo.create(cart=cart, product=product, quantity=data.quantity)
            await self.cart_repo.update_amount(cart=cart)

            return StringResponse(detail="Product added to your cart!")

    async def get_history(self, user: TokenData) -> list[CartData]:
        carts = await self.cart_repo.get_all(user_id=user.id)
        return [CartData.model_validate(cart, from_attributes=True) for cart in carts]

    async def history_detail(self, cart_id: UUID, user: TokenData) -> CartDetail | Exception:
        cart = await self.cart_repo.get(id=cart_id, user_id=user.id)
        if not cart:
            raise CartNotFoundError(f"Cart with id `{cart_id}` not found!")

        items = [CartItemData.model_validate(item, from_attributes=True) for item in cart.items]

        return CartDetail(cart=cart, items=items)

    async def delete_item(self, item_id: UUID, user: TokenData) -> StringResponse | Exception:
        async with self.cart_item_repo.db.begin():
            item = await self.cart_item_repo.get(id=item_id, cart_status=False)
            if not item:
                raise ItemNotFoundError(f"Item with id `{item_id}` not found!")

            cart = await self.cart_repo.get(id=item.cart_id, user_id=user.id)

            if not cart:
                raise CartNotFoundError(f"Cart not found!")
            elif cart.status:
                raise AlreadyPaidError("Cart Already paid!")

            await self.cart_item_repo.delete_cart_item(item=item)

            return StringResponse(detail="Item deleted successfuly!")


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.cart_repo = CartRepository(db=db)
        self.payment_repo = PaymentRepository(db=db)

    async def open_gate(self, cart_id: UUID, user: TokenData) -> StringResponse | Exception:
        async with self.cart_repo.db.begin():
            cart = await self.cart_repo.get(id=cart_id, user_id=user.id)
            if not cart:
                raise CartNotFoundError(f"Cart with id `{cart_id}` not found!")

            elif cart.status:
                raise AlreadyPaidError("your cart has been already paied!")

            elif cart.amount <= 0:
                raise EmptyCartError("Your cart has been empty!")

            result = await self.payment_repo.open_gate(cart=cart)
            if not result.get("success"):
                raise GatewayError("Error in open gate!")

            return StringResponse(detail=result.get("url"))

    async def verify_payment(self, status: str, authority: str) -> StringResponse | Exception:
        if status != "OK":
            raise PaymentFailed("Payment failed!")

        cart = await self.cart_repo.get(authority=authority)
        if not cart:
            raise CartNotFoundError("Cart not found!")

        verify = await self.payment_repo.verify_payment(cart=cart)

        if not verify.get("success"):
            raise PaymentFailed()

        return StringResponse(detail="http://localhost:8000")
