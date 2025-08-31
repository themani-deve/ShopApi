from uuid import UUID

from account.schemas import StringResponse, TokenData
from product.exception import ProductNotFoundError
from product.repositories import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import CartNotFoundError
from .repositories import CartItemRepository, CartRepository
from .schemas import CartData, CartDetail, CartItemData, AddCartItem


class CartService:
    def __init__(self, db: AsyncSession):
        self.cart_repo = CartRepository(db=db)
        self.cart_item_repo = CartItemRepository(db=db)
        self.product_repo = ProductRepository(db=db)

    async def add(self, user: TokenData, product_id: UUID, data: AddCartItem) -> StringResponse:
        async with self.cart_repo.db.begin():
            cart = await self.cart_repo.get(user_id=user.id, status=False)
            if not cart:
                cart = await self.cart_repo.create(user_id=user.id)

            product = await self.product_repo.get(id=product_id)
            if not product:
                raise ProductNotFoundError(f"Product with id `{product_id}` not found!")

            await self.cart_item_repo.create(cart=cart, product=product, quantity=data.quantity)
            await self.cart_repo.update_amount(cart_id=cart.id)

            return StringResponse(detail="Product added to your cart!")

    async def get_history(self, user: TokenData) -> list[CartData]:
        carts = await self.cart_repo.get_all(user_id=user.id)
        return [CartData.model_validate(cart, from_attributes=True) for cart in carts]
    
    async def history_detail(self, cart_id: UUID, user: TokenData) -> CartDetail:
        cart = await self.cart_repo.get(id=cart_id, user_id=user.id)
        if not cart:
            raise CartNotFoundError(f"Cart with id `{cart_id}` not found!")

        items = [CartItemData.model_validate(item, from_attributes=True) for item in cart.items]

        return CartDetail(cart=cart, items=items)
