from datetime import date

from src.core.exceptions.booking import (
    BookingNotFoundException,
    BookingOutsideSlotException,
    BookingOverlapException,
)
from src.core.exceptions.user import ForbiddenException
from src.db.repositories.booking import BookingRepository
from src.db.repositories.room import RoomRepository
from src.db.repositories.slot import SlotRepository
from src.db.repositories.user import UserRepository
from src.models.booking import Booking
from src.models.enums import UserRole
from src.models.user import User
from src.schemas.booking import (
    BookingAdminResponse,
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from src.services.room import RoomService
from src.services.user import UserService


class BookingService:
    def __init__(
        self,
        booking_repo: BookingRepository,
        room_repo: RoomRepository,
        slot_repo: SlotRepository,
        user_repo: UserRepository,
    ):
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.slot_repo = slot_repo
        self.user_repo = user_repo

    async def create_booking(
        self,
        booking_in: BookingCreate,
        current_user: User,
    ) -> BookingResponse:
        room_service = RoomService(
            room_repo=self.room_repo,
            slot_repo=self.slot_repo,
            booking_repo=self.booking_repo,
        )
        await room_service.get_room_by_id(booking_in.room_id)

        if not await self.slot_repo.is_booking_available(
            booking_in.room_id,
            booking_in.start_time,
            booking_in.end_time,
        ):
            raise BookingOutsideSlotException()

        if not await self.booking_repo.is_booking_available(
            booking_in.room_id,
            booking_in.start_time,
            booking_in.end_time,
        ):
            raise BookingOverlapException()

        booking_data = booking_in.model_dump()
        booking_data["user_id"] = current_user.id
        booking = await self.booking_repo.create(booking_data)

        return BookingResponse.model_validate(booking)

    async def _get_bookings(
        self,
        room_id: int | None,
        user_id: int | None,
        date_in: date | None,
    ) -> list[Booking]:
        if room_id:
            room_service = RoomService(
                room_repo=self.room_repo,
                slot_repo=self.slot_repo,
                booking_repo=self.booking_repo,
            )
            await room_service.get_room_by_id(room_id)
        if user_id:
            user_service = UserService(self.user_repo)
            await user_service.get_user_by_id(user_id)

        return await self.booking_repo.get_multi(room_id, user_id, date_in)

    async def get_bookings(
        self,
        room_id: int | None,
        user_id: int | None,
        date_in: date | None,
    ) -> list[BookingResponse]:
        bookings = await self._get_bookings(room_id, user_id, date_in)
        return [BookingResponse.model_validate(booking) for booking in bookings]

    async def get_bookings_admin(
        self,
        room_id: int | None,
        user_id: int | None,
        date_in: date | None,
    ) -> list[BookingAdminResponse]:
        bookings = await self._get_bookings(room_id, user_id, date_in)
        return [BookingAdminResponse.model_validate(booking) for booking in bookings]

    async def _update(
        self,
        booking_id: int,
        booking_in: BookingUpdate,
        current_user: User,
    ) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundException()

        if current_user.id != booking.user_id and current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Not permission to update this booking")

        if booking_in.room_id:
            room_service = RoomService(
                room_repo=self.room_repo,
                slot_repo=self.slot_repo,
                booking_repo=self.booking_repo,
            )
            await room_service.get_room_by_id(booking_in.room_id)

        update_data = booking_in.model_dump(exclude_unset=True)

        room_id = booking_in.room_id or booking.room_id
        start_time = booking_in.start_time or booking.start_time
        end_time = booking_in.end_time or booking.end_time

        booking_in.start_time = start_time
        booking_in.end_time = end_time
        booking_in = booking_in.model_validate(booking_in.model_dump())

        if not await self.slot_repo.is_booking_available(room_id, start_time, end_time):
            raise BookingOutsideSlotException()

        if not await self.booking_repo.is_booking_available(
            room_id,
            start_time,
            end_time,
            booking.id,
        ):
            raise BookingOverlapException()

        booking = await self.booking_repo.update(booking_id, update_data)
        if booking is None:
            raise BookingNotFoundException()

        return booking

    async def update_booking(
        self,
        booking_id: int,
        booking_in: BookingUpdate,
        current_user: User,
    ) -> BookingResponse:
        booking = await self._update(booking_id, booking_in, current_user)
        return BookingResponse.model_validate(booking)

    async def update_booking_admin(
        self,
        booking_id: int,
        booking_in: BookingUpdate,
        current_user: User,
    ) -> BookingAdminResponse:
        booking = await self._update(booking_id, booking_in, current_user)
        return BookingAdminResponse.model_validate(booking)

    async def delete_booking(self, booking_id: int, current_user: User):
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundException()

        if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Not permission to delete this booking")

        await self.booking_repo.delete(booking_id)
