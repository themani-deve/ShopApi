import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))

    name: Mapped[str] = mapped_column(String(48), nullable=True)
    family: Mapped[str] = mapped_column(String(58), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=True, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean(), default=False)
    key: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)

    join_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)

    products: Mapped[list["Product"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    carts: Mapped[list["Cart"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["ProductComment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def to_payload(self):
        return {"id": str(self.id), "email": self.email, "is_active": self.is_active, "is_staff": self.is_staff}

    @property
    def get_full_name(self):
        return f"{self.name or ''} {self.family or ''}".strip()


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[int] = mapped_column(Integer(), default=0)
    discount: Mapped[int] = mapped_column(Integer(), default=0)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)

    count: Mapped[int] = mapped_column(Integer(), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="products")

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    comments: Mapped[list["ProductComment"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("price >= 0 ", name="product_price_min"),
        CheckConstraint("discount >= 0 ", name="product_discount_min"),
        CheckConstraint("discount <= 100 ", name="product_discount_max"),
    )

    @property
    def get_price(self):
        if self.discount and 0 <= self.discount <= 100:
            discount_rate = self.discount / 100
            multiplier = 1 - discount_rate
            final_price = multiplier * self.price
            return final_price
        return self.price


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


class ProductComment(Base):
    __tablename__ = "product_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    text: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="comments")

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="comments")

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_comments.id"), nullable=True
    )
    parent: Mapped["ProductComment"] = relationship(back_populates="replies", remote_side="ProductComment.id")

    replies: Mapped[list["ProductComment"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
