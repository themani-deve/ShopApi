import uuid

from account.exceptions import UserIsNotAdminError, UserNotFoundError
from account.repositories import AccountRepository
from account.schemas import StringResponse, TokenData
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generators import slugify

from .exception import ProductNotFoundError
from .repositories import ProductRepository
from .schemas import CreateProduct, ProductData, ProductDetail, UserStatus


class ProductService:
    def __init__(self, db: AsyncSession):
        self.product_repo = ProductRepository(db=db)
        self.account_repo = AccountRepository(db=db)

    async def get_all(self) -> list[ProductData]:
        products = await self.product_repo.get_all()
        return [ProductData.model_validate(product, from_attributes=True) for product in products]

    async def product_detail(self, slug: str, user=None) -> ProductDetail:
        product = await self.product_repo.get(slug=slug, is_active=True)
        if not product:
            raise ProductNotFoundError(f"Product with slug `{slug}` not found!")

        need_login = True
        in_cart = False

        if user:
            need_login = False

        product = ProductData.model_validate(product)
        user_status = UserStatus(need_login=need_login, in_cart=in_cart)

        return ProductDetail(product=product, user_status=user_status)

    async def create_product(self, data: CreateProduct, user: TokenData) -> StringResponse:
        async with self.product_repo.db.begin():
            user = await self.account_repo.get(id=user.id)
            if not user:
                raise UserNotFoundError("User not found!")

            elif not user.is_staff:
                raise UserIsNotAdminError("You do not permission for this action!")

            base_slug = slugify(data.name)
            slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            product = await self.product_repo.create(
                name=data.name,
                price=data.price,
                discount=data.discount,
                count=data.count,
                is_active=data.is_active,
                slug=slug,
                owner=user,
            )

            return StringResponse(detail=f"Product with id `{product.id}` created successfully!")

    async def delete_product(self, product_id: uuid.UUID, user: TokenData) -> StringResponse:
        async with self.product_repo.db.begin():
            product = await self.product_repo.get(id=product_id, owner_id=user.id)
            if not product:
                raise ProductNotFoundError("Product not found!")

            await self.product_repo.delete()

            return StringResponse(detail=f"Product with id `{product_id}` deleted successfuly!")
