from repositories.product import ProductRepository
from repositories.user import UserRepository
from schemas.product import *
from schemas.user import TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    @staticmethod
    async def create(session: AsyncSession, token: TokenDataSchema, data: CreateProductInputSchema):
        user = await UserRepository.find(session=session, id=token.id, is_active=True, is_staff=True)

        if not user:
            return None

        data = data.model_dump()
        data["owner_id"] = user.id
        product = await ProductRepository.create(session=session, data=data)

        return product

    @staticmethod
    async def products(session: AsyncSession):
        products = await ProductRepository.get_all(session=session)
        for product in products:
            print(product.name)
        return products

    @staticmethod
    async def product_detail(session: AsyncSession, slug: str, token: TokenDataSchema = None):
        if token:
            pass

        product_obj = await ProductRepository.find(session=session, slug=slug)

        product_dict = ProductSchema.model_validate(product_obj, from_attributes=True)
        product_user = UserStatusSchema(in_cart=True, need_login=False)

        product = ProductDetailSchema(product=product_dict, user_status=product_user)

        return product
