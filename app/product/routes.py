from uuid import UUID

from account.schemas import StringResponse, TokenData
from core.dependencies.user import is_admin, login_optional
from db.database import get_db
from fastapi import Body, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CreateProduct, ProductData, ProductDetail
from .services import ProductService

route = APIRouter()


@route.get("", response_model=list[ProductData], tags=["Product"])
async def get_all(db: AsyncSession = Depends(get_db)):
    service = ProductService(db=db)
    return await service.get_all()


@route.get("/detail/{slug}", response_model=ProductDetail, tags=["Product"])
async def product_detail(slug: str, db: AsyncSession = Depends(get_db), user: TokenData = Depends(login_optional)):
    service = ProductService(db=db)
    return await service.product_detail(slug=slug, user=user)


@route.post("/create", response_model=StringResponse, tags=["Product"])
async def create(db: AsyncSession = Depends(get_db), user: TokenData = Depends(is_admin), data: CreateProduct = Body()):
    service = ProductService(db=db)
    return await service.create_product(data=data, user=user)


@route.delete("/delete/{product_id}", response_model=StringResponse, tags=["Product"])
async def delete(product_id: UUID, db: AsyncSession = Depends(get_db), user: TokenData = Depends(is_admin)):
    service = ProductService(db=db)
    return await service.delete_product(product_id=product_id, user=user)
