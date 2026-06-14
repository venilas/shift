from datetime import date
from zoneinfo import ZoneInfo

from src.config.settings import get_settings
from src.core.exceptions.room import RoomNotFoundException
from src.db.repositories.booking import BookingRepository
from src.db.repositories.room import RoomRepository
from src.db.repositories.slot import SlotRepository
from src.models.booking import Booking
from src.models.slot import Slot
from src.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from src.schemas.slot import SlotAvailability


class RoomService:
    def __init__(
        self,
        room_repo: RoomRepository,
        slot_repo: SlotRepository,
        booking_repo: BookingRepository,
    ):
        self.room_repo = room_repo
        self.slot_repo = slot_repo
        self.booking_repo = booking_repo

    async def create_room(self, room_in: RoomCreate) -> RoomResponse:
        room = await self.room_repo.create(room_in.model_dump())
        return RoomResponse.model_validate(room)

    async def get_rooms(
        self,
        offset: int,
        limit: int,
        floor: int | None,
    ) -> tuple[list[RoomResponse], int]:
        rooms_in_db = await self.room_repo.get_multi(offset, limit, floor)
        rooms = [RoomResponse.model_validate(room) for room in rooms_in_db]
        total = await self.room_repo.count()
        return rooms, total

    def _get_slots_availability(
        self,
        date_in: date,
        slots: list[Slot],
        bookings: list[Booking],
    ) -> list[dict]:
        if not bookings:
            return [
                {
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                }
                for slot in slots
            ]

        tz = ZoneInfo(key=get_settings().TIMEZONE)
        free = []
        for slot in slots:
            current = slot.start_time

            for booking in bookings:
                booking.start_time = booking.start_time.astimezone(tz=tz)
                booking.end_time = booking.end_time.astimezone(tz=tz)

                if booking.start_time.date() > date_in:
                    continue

                if (
                    booking.end_time.time() <= slot.start_time
                    or booking.start_time.time() >= slot.end_time
                ):
                    continue

                booking_start = max(booking.start_time.time(), slot.start_time)
                booking_end = min(booking.end_time.time(), slot.end_time)

                if booking_start > current:
                    free.append({"start_time": current, "end_time": booking_start})

                current = max(current, booking_end)

            if current < slot.end_time:
                free.append({"start_time": current, "end_time": slot.end_time})

        return free

    async def get_room_availability(
        self,
        room_id: int,
        date_in: date,
    ) -> list[SlotAvailability]:
        await self.get_room_by_id(room_id)

        slots = await self.slot_repo.get_multi(room_id)
        bookings = await self.booking_repo.get_multi(
            room_id,
            user_id=None,
            date_in=date_in,
        )

        slots_availability = self._get_slots_availability(date_in, slots, bookings)

        return [SlotAvailability(**slot) for slot in slots_availability]

    async def get_room_by_id(self, room_id: int) -> RoomResponse:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException()
        return RoomResponse.model_validate(room)

    async def update_room(self, room_id: int, room_in: RoomUpdate) -> RoomResponse:
        await self.get_room_by_id(room_id)

        update_data = room_in.model_dump(exclude_unset=True)

        room = await self.room_repo.update(room_id, update_data)
        return RoomResponse.model_validate(room)

    async def delete_room(self, room_id: int) -> None:
        await self.get_room_by_id(room_id)
        await self.room_repo.delete(room_id)
