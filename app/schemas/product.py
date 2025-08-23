from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductOwnerSchema(BaseModel):
    email: str
    name: Optional[str]
    family: Optional[str]
    phone_number: Optional[str]


class CreateProductInputSchema(BaseModel):
    name: str
    price: int
    discount: int = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    count: int = Field(..., ge=0)
    is_active: bool = True


class CreateProductResponseSchema(BaseModel):
    name: str
    price: int
    discount: int
    count: int
    is_active: bool
    slug: str
    created_at: datetime
    owner: ProductOwnerSchema

    class Config:
        from_attributes = True


class UserStatusSchema(BaseModel):
    in_cart: bool = False
    need_login: bool = True


class ProductSchema(BaseModel):
    id: UUID
    name: str
    price: int
    discount: int
    slug: str
    count: int
    is_active: bool
    owner: Optional[ProductOwnerSchema]

    class Config:
        from_attributes = True


class ProductDetailSchema(BaseModel):
    product: ProductSchema
    user_status: UserStatusSchema

    class Config:
        from_attributes = True


class CartItemSchema(BaseModel):
    id: UUID
    quantity: int
    product: ProductSchema

    class Config:
        from_attributes = True


class AddCartInputSchema(BaseModel):
    quantity: int = Field(default=1, ge=1, description="Quantity greater than or equal to one")


class AddCartResponseSchema(BaseModel):
    id: UUID
    items: List[CartItemSchema]

    class Config:
        from_attributes = True
