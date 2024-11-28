import enum
import uuid
from datetime import date
from typing import Optional
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import Boolean, Date, ForeignKey, String, DateTime, DateTime, func, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class Contact(Base):
    __tablename__ = "contacts"
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    email_sec: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True, default=None)
    date_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")

    @hybrid_property
    def fullname(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    last_visit: Mapped[date] = mapped_column(
        "last_visit", DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
