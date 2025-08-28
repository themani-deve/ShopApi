import uuid
from datetime import datetime

from db.database import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    status: Mapped[bool] = mapped_column(Boolean(), default=False)
    authority: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    ref_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    amount: Mapped[int] = mapped_column(Integer(), default=0)

    paid_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="carts")

    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    quantity: Mapped[int] = mapped_column(Integer(), default=0)

    cart_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("carts.id"))
    cart: Mapped["Cart"] = relationship(back_populates="items")

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="cart_items")
