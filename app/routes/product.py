from typing import Optional

from core.dependencies.user import is_admin, login_optional
from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas.product import *
from schemas.user import TokenDataSchema
from services.product import ProductService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.get("", response_model=list[ProductSchema], tags=["Product"])
async def products(session: AsyncSession = Depends(get_db)):
    products = await ProductService.products(session=session)
    return products


@route.get("/{slug}", response_model=ProductDetailSchema, tags=["Product"])
async def product_detail(
    slug: str, session: AsyncSession = Depends(get_db), token: Optional[TokenDataSchema] = Depends(login_optional)
):
    product = await ProductService.product_detail(session=session, slug=slug, token=token)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@route.post("/create", response_model=CreateProductResponseSchema, tags=["Product"])
async def create(
    token: TokenDataSchema = Depends(is_admin),
    session: AsyncSession = Depends(get_db),
    data: CreateProductInputSchema = Body(),
):
    product = await ProductService.create(session=session, token=token, data=data)

    if not product:
        raise HTTPException(status_code=400, detail="Product already exists")

    return product
