from pydantic import BaseModel, Field
from uuid import UUID
from account.schemas import UserData


class CreateProduct(BaseModel):
    name: str
    price: int
    discount: int = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    count: int = Field(..., ge=0)
    is_active: bool = True


class ProductData(BaseModel):
    id: UUID
    name: str
    price: int
    discount: int
    count: int
    is_active: bool
    slug: str
    owner: UserData

    class Config:
        from_attributes = True


class UserStatus(BaseModel):
    need_login: bool = True
    in_cart: bool = False


class ProductDetail(BaseModel):
    product: ProductData
    user_status: UserStatus
