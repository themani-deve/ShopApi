from uuid import UUID

from account.schemas import StringResponse, TokenData
from core.dependencies.user import get_user
from db.database import get_db
from fastapi import Body, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import AddCartItem, CartData, CartDetail
from .services import CartService

route = APIRouter()


@route.post("/add/{product_id}", response_model=StringResponse, tags=["Cart"])
async def add_to_cart(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenData = Depends(get_user),
    data: AddCartItem = Body(),
):
    service = CartService(db=db)
    return await service.add(user=user, product_id=product_id, data=data)


@route.get("/history", response_model=list[CartData], tags=["Cart"])
async def get_history(db: AsyncSession = Depends(get_db), user: TokenData = Depends(get_user)):
    service = CartService(db=db)
    return await service.get_history(user=user)


@route.get("/history/{cart_id}", response_model=CartDetail, tags=["Cart"])
async def history_detail(cart_id: UUID, db: AsyncSession = Depends(get_db), user: TokenData = Depends(get_user)):
    service = CartService(db=db)
    return await service.history_detail(cart_id=cart_id, user=user)
