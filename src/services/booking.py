from datetime import datetime

from src.core.exceptions.booking import (
    BookingNotAvailableException,
    BookingNotFoundException,
)
from src.core.exceptions.slot import SlotNotAvailableException
from src.core.exceptions.user import ForbiddenException
from src.db.repositories.booking import BookingRepository
from src.db.repositories.slot import SlotRepository
from src.models.enums import UserRole
from src.models.user import User
from src.schemas.booking import BookingCreate, BookingResponse, BookingUpdate


class BookingService:
    def __init__(self, booking_repo: BookingRepository, slot_repo: SlotRepository):
        self.booking_repo = booking_repo
        self.slot_repo = slot_repo

    async def create(
        self,
        booking_in: BookingCreate,
        current_user: User,
    ) -> BookingResponse:
        if not await self.booking_repo.is_booking_available(
            booking_in.room_id,
            booking_in.start_time,
            booking_in.end_time,
        ):
            raise BookingNotAvailableException()

        if not await self.slot_repo.is_booking_available(
            booking_in.room_id,
            booking_in.start_time,
            booking_in.end_time,
        ):
            raise SlotNotAvailableException()

        booking_data = booking_in.model_dump()
        booking_data["user_id"] = current_user.id
        booking = await self.booking_repo.create(booking_data)
        return BookingResponse.model_validate(booking)

    async def delete(self, booking_id: int, current_user: User):
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundException()

        if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Not authorized to delete this booking")

        await self.booking_repo.delete(booking_id)

    async def get_bookings(
        self,
        room_id: int | None,
        user_id: int | None,
        date: datetime | None,
    ) -> list[BookingResponse]:
        bookings = await self.booking_repo.get_bookings(room_id, user_id, date)
        return [BookingResponse.model_validate(booking) for booking in bookings]

    async def update(
        self,
        booking_id: int,
        booking_in: BookingUpdate,
        current_user: User,
    ) -> BookingResponse:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundException()

        if current_user.id != booking.user_id and current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Not authorized to update this booking")

        update_data = booking_in.model_dump(exclude_unset=True)

        room_id = booking_in.room_id or booking.room_id
        start_time = booking_in.start_time or booking.start_time
        end_time = booking_in.end_time or booking.end_time

        booking_in.start_time = start_time
        booking_in.end_time = end_time
        booking_in = booking_in.model_validate(booking_in.model_dump())

        if not await self.booking_repo.is_booking_available(
            room_id,
            start_time,
            end_time,
            booking.id,
        ):
            raise BookingNotAvailableException()

        if not await self.slot_repo.is_booking_available(room_id, start_time, end_time):
            raise SlotNotAvailableException()

        booking = await self.booking_repo.update(booking_id, update_data)
        return BookingResponse.model_validate(booking)
