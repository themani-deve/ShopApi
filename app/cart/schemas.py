from datetime import datetime
from typing import Optional
from uuid import UUID

from product.schemas import ProductData
from pydantic import BaseModel, Field


class AddCartItem(BaseModel):
    quantity: int = Field(1, ge=0, description="Quantity must be more than 0")


class CartData(BaseModel):
    id: UUID
    status: bool
    amount: int
    ref_id: Optional[str]
    paid_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemData(BaseModel):
    id: UUID
    quantity: int
    product: ProductData

    class Config:
        from_attributes = True


class CartDetail(BaseModel):
    cart: CartData
    items: Optional[list[CartItemData]]
