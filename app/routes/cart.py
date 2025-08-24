from uuid import UUID

from core.dependencies.user import get_current_user
from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas.cart import AddCartInputSchema, CartResponseSchema
from schemas.user import TokenDataSchema
from services.cart import CartService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.get("", response_model=CartResponseSchema, tags=["Cart"])
async def cart(session: AsyncSession = Depends(get_db), user: TokenDataSchema = Depends(get_current_user)):
    cart = await CartService.get_cart_items(session=session, user=user)

    if not cart:
        raise HTTPException(status_code=400, detail="User not found or account not activated")

    return cart


@route.post("/add/{product_id}", tags=["Cart"])
async def add_to_cart(
    product_id: UUID,
    session: AsyncSession = Depends(get_db),
    user: TokenDataSchema = Depends(get_current_user),
    data: AddCartInputSchema = Body(),
):
    response = await CartService.add(
        session=session,
        user=user,
        product_id=product_id,
        quantity=data.quantity,
    )

    if not response:
        raise HTTPException(status_code=400, detail="There was a problem")

    return {"detail": "Product added to your cart successfuly"}


@route.delete("/delete-item/{item_id}", tags=["Cart"])
async def delete_item(
    item_id: UUID, session: AsyncSession = Depends(get_db), user: TokenDataSchema = Depends(get_current_user)
):
    deleted = await CartService.delete_item(session=session, user=user, item_id=item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"detail": "Item deleted successfuly"}
