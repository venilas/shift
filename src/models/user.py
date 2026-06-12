from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.booking import Booking
from src.models.enums import UserRole


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(length=50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=64), nullable=False)
    hashed_password = mapped_column(String(length=255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=5),
        default=UserRole.USER,
        nullable=False,
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
