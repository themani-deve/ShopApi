from repositories.product import ProductRepository
from repositories.user import UserRepository
from schemas.product import *
from schemas.response import ServiceResult
from schemas.user import TokenDataSchema
from services.cart import CartService
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    @staticmethod
    async def get_products(session: AsyncSession) -> ServiceResult:
        products = await ProductRepository.get_all(session=session)
        return ServiceResult(success=True, data=products)

    @staticmethod
    async def product_detail(session: AsyncSession, slug: str, user: TokenDataSchema = None) -> ServiceResult:
        in_cart = False
        need_login = True

        product_obj = await ProductRepository.find(session=session, slug=slug, is_active=True)
        if not product_obj:
            return ServiceResult(success=False, message="Product not found", status_code=404)

        if user:
            need_login = False
            in_cart = await CartService.user_status(session=session, user=user, product_id=product_obj.id)

        product_dict = ProductSchema.model_validate(product_obj, from_attributes=True)
        product_user = UserStatusSchema(in_cart=in_cart, need_login=need_login)

        product = ProductDetailSchema(product=product_dict, user_status=product_user)

        return ServiceResult(success=True, data=product)

    @staticmethod
    async def create(session: AsyncSession, user: TokenDataSchema, data: CreateProductInputSchema) -> ServiceResult:
        user = await UserRepository.get_active_user(session=session, user_id=user.id)
        if not user:
            return ServiceResult(success=False, message="User not found", status_code=404)

        data = data.model_dump()
        data["owner_id"] = user.id
        product = await ProductRepository.create(session=session, data=data)

        return ServiceResult(success=True, data=product)

    @staticmethod
    async def delete(session: AsyncSession, user: TokenDataSchema, product_id: UUID) -> ServiceResult:
        product = await ProductRepository.find(session=session, id=product_id, owner_id=user.id)
        if not product:
            return ServiceResult(success=False, message="Product not found", status_code=404)

        await ProductRepository.delete(session=session, product_id=product.id)

        return ServiceResult(success=True, message="Product deleted successfuly")
