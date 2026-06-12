from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin
from src.models.booking import Booking
from src.models.slot import Slot


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(length=100), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)

    slots: Mapped[list["Slot"]] = relationship(back_populates="room")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")
