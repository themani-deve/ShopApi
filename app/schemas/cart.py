from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .product import ProductSchema


class AddCartInputSchema(BaseModel):
    quantity: int = Field(default=1, ge=1, description="Quantity greater than or equal to one")


class CartItemSchema(BaseModel):
    id: UUID
    quantity: int
    product: ProductSchema

    class Config:
        from_attributes = True


class CartSchema(BaseModel):
    id: UUID
    status: bool
    ref_id: Optional[str]
    amount: Optional[int]
    paid_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class CartResponseSchema(BaseModel):
    cart: CartSchema
    items: Optional[List[CartItemSchema]]

    class Config:
        from_attributes = True
