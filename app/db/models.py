import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    name: Mapped[str] = mapped_column(String(48), nullable=True)
    family: Mapped[str] = mapped_column(String(58), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=True, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    key: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)

    join_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)

    @property
    def to_payload(self):
        return {"id": str(self.id), "email": self.email, "is_active": self.is_active}

    @property
    def get_full_name(self):
        return f"{self.name or ''} {self.family or ''}".strip()
