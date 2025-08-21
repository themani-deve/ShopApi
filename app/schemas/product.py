import uuid
from typing import Optional

from pydantic import BaseModel, Field


class CreateProductSchema(BaseModel):
    name: str
    price: int
    discount: int = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    count: int = Field(..., ge=0)
    is_active: bool = True


class ProductOwnerSchema(BaseModel):
    email: str
    name: Optional[str]
    family: Optional[str]
    phone_number: Optional[str]


class ProductResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    price: int
    discount: int
    slug: str
    count: int
    is_active: bool
    owner: Optional[ProductOwnerSchema]

    class Config:
        from_attributes = True
