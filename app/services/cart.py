from uuid import UUID

from repositories.cart import CartPaymentRepository, CartRepository
from repositories.product import ProductRepository
from repositories.user import UserRepository
from schemas.cart import CartResponseSchema, PayResponseSchema
from schemas.response import ServiceResult
from schemas.user import TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession


class CartService:
    @staticmethod
    async def get_cart_items(session: AsyncSession, user: TokenDataSchema) -> ServiceResult:
        user = await UserRepository.get_active_user(session, user.id)
        if not user:
            return ServiceResult(success=False, message="User not found", status_code=404)

        cart = await CartRepository.create_cart(session=session, user_id=user.id)

        response = CartResponseSchema(cart=cart, items=cart.items)

        return ServiceResult(success=True, data=response)

    @staticmethod
    async def add(session: AsyncSession, user: TokenDataSchema, product_id: UUID, quantity: int) -> ServiceResult:
        user = await UserRepository.get_active_user(session, user.id)
        if not user:
            return ServiceResult(success=False, message="User not found", status_code=404)

        product = await ProductRepository.find(session=session, id=product_id, is_active=True)
        if not product:
            return ServiceResult(success=False, message="Product not found", status_code=404)

        cart = await CartRepository.create_cart(session=session, user_id=user.id)
        if not cart:
            return ServiceResult(success=False, message="Cart not found", status_code=404)

        await CartRepository.add(session=session, cart_id=cart.id, product_id=product.id, quantity=quantity)
        await CartRepository.update_cart_amount(session=session, cart=cart)

        return ServiceResult(success=True, message="Product added to your cart successfuly", status_code=201)

    @staticmethod
    async def history(session: AsyncSession, user: TokenDataSchema) -> ServiceResult:
        carts = await CartRepository.get_history(session=session, user_id=user.id)
        return ServiceResult(success=True, data=carts)

    @staticmethod
    async def history_detail(session: AsyncSession, user: TokenDataSchema, cart_id: UUID) -> ServiceResult:
        cart = await CartRepository.find_cart(session=session, user_id=user.id, id=cart_id)
        if not cart:
            return ServiceResult(success=False, message="Cart not found", status_code=404)

        response = CartResponseSchema(cart=cart, items=cart.items)

        return ServiceResult(success=True, data=response)

    @staticmethod
    async def delete_item(session: AsyncSession, user: TokenDataSchema, item_id: UUID) -> ServiceResult:
        cart = await CartRepository.find_cart(session=session, user_id=user.id, status=False)
        if not cart:
            return ServiceResult(success=False, message="Cart not found", status_code=404)

        item = await CartRepository.find_item(session=session, id=item_id, cart_id=cart.id)
        if not item:
            return ServiceResult(success=False, message="Item not found", status_code=404)

        await CartRepository.delete_item(session=session, item_id=item.id)
        await CartRepository.update_cart_amount(session=session, cart=cart)

        return ServiceResult(success=True, message="Item deleted successfuly")

    @staticmethod
    async def user_status(session: AsyncSession, user: TokenDataSchema, product_id: UUID) -> bool:
        cart = await CartRepository.create_cart(session=session, user_id=user.id)
        return any(item.product_id == product_id for item in cart.items)


class CartPaymentService:
    @staticmethod
    async def open_gate(session: AsyncSession, user: TokenDataSchema, cart_id: UUID) -> ServiceResult:
        cart = await CartRepository.find_cart(session=session, user_id=user.id, id=cart_id)
        if not cart:
            return ServiceResult(success=False, message="Cart not found", status_code=404)

        if cart.status:
            return ServiceResult(success=False, message="The shopping cart has already been paid for", status_code=400)

        if not cart.amount or cart.amount <= 0:
            return ServiceResult(success=False, message="Shopping cart is empty", status_code=400)

        result = await CartPaymentRepository.open_gate(session=session, cart=cart)

        if not result.get("success"):
            return ServiceResult(success=False, message="Error in open gate", status_code=400)

        response = PayResponseSchema(url=result.get("url"))

        return ServiceResult(success=True, data=response)

    @staticmethod
    async def verify_payment(session: AsyncSession, status: str, authority: str) -> ServiceResult:
        if status != "OK":
            return ServiceResult(success=False, message="Payment failed", status_code=400)

        cart = await CartRepository.find_cart(session=session, authority=authority)
        if not cart:
            return ServiceResult(success=False, message="Cart not found", status_code=404)

        verify = await CartPaymentRepository.verify_payment(session=session, cart=cart)

        if not verify.get("success"):
            return ServiceResult(success=False, message=verify["message"], status_code=400)

        response = PayResponseSchema(url="http://localhost:8000")

        return ServiceResult(success=True, data=response)
