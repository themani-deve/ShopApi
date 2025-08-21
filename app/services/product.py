from repositories.product import CreateProductSchema, ProductRepository
from repositories.user import UserRepository
from schemas.user import TokenDataSchema
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    @staticmethod
    async def create(session: AsyncSession, token: TokenDataSchema, data: CreateProductSchema):
        user = await UserRepository.find(session=session, id=token.id)
        if not user:
            return None

        data = data.dict()
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
    async def product_detail(session: AsyncSession, slug: str):
        product = await ProductRepository.find(session=session, slug=slug)
        return product
