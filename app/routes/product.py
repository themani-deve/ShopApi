from typing import Optional

from core.dependencies.user import get_current_user, is_admin, login_optional
from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas.product import *
from schemas.user import TokenDataSchema
from services.product import ProductCommentService, ProductService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.get("", response_model=list[ProductSchema], tags=["Product"])
async def products(session: AsyncSession = Depends(get_db)):
    response = await ProductService.get_products(session=session)
    return response.data


@route.get("/detail/{slug}", response_model=ProductDetailSchema, tags=["Product"])
async def product_detail(
    slug: str, session: AsyncSession = Depends(get_db), user: Optional[TokenDataSchema] = Depends(login_optional)
):
    response = await ProductService.product_detail(session=session, slug=slug, user=user)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return response.data


@route.post("/create", response_model=CreateProductResponseSchema, tags=["Product"])
async def create(
    user: TokenDataSchema = Depends(is_admin),
    session: AsyncSession = Depends(get_db),
    data: CreateProductInputSchema = Body(),
):
    response = await ProductService.create(session=session, user=user, data=data)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return response.data


@route.delete("/delete/{product_id}", tags=["Product"])
async def delete(
    product_id: UUID, session: AsyncSession = Depends(get_db), user: TokenDataSchema = Depends(get_current_user)
):
    response = await ProductService.delete(session=session, user=user, product_id=product_id)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}


@route.post("/comments/add/{product_id}", response_model=ProductCommentResponseSchema, tags=["Product Comments"])
async def add_comment(
    product_id: UUID,
    session: AsyncSession = Depends(get_db),
    user: TokenDataSchema = Depends(get_current_user),
    data: ProductCommentInputSchema = Body(),
):
    response = await ProductCommentService.add_comment(
        session=session, user=user, product_id=product_id, text=data.text, parent_id=data.parent_id
    )

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)
    
    return response.data
