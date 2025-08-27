from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from schemas.user import UserSchema


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
    owner: UserSchema

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
    owner: Optional[UserSchema]

    class Config:
        from_attributes = True


class ProductCommentInputSchema(BaseModel):
    text: str
    parent_id: Optional[UUID] = None


class ProductCommentResponseSchema(BaseModel):
    id: UUID
    text: str
    parent_id: Optional[UUID] = None
    user: UserSchema

    class Config:
        from_attributes = True


class ProductDetailSchema(BaseModel):
    product: ProductSchema
    user_status: UserStatusSchema
    product_comments: Optional[list[ProductCommentResponseSchema]]

    class Config:
        from_attributes = True
