from datetime import date
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.models.booking import Booking
from src.models.room import Room
from src.models.slot import Slot


class RoomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, room_in: dict) -> Room:
        room = Room(**room_in)
        self.session.add(room)
        await self.session.flush()
        await self.session.refresh(room)
        return room

    async def get_by_id(self, room_id: int) -> Room | None:
        query = select(Room).where(Room.id == room_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, room_id: int, room_in: dict) -> Room | None:
        room = await self.get_by_id(room_id)
        if not room:
            return None

        for key, value in room_in.items():
            if getattr(room, key, None):
                setattr(room, key, value)

        self.session.add(room)
        await self.session.flush()
        return room

    async def delete(self, room_id: int) -> None:
        query = delete(Room).where(Room.id == room_id)
        await self.session.execute(query)

    async def get_rooms(self, offset: int, limit: int, floor: int | None) -> list[Room]:
        query = select(Room).offset(offset).limit(limit).order_by(Room.id)
        if floor:
            query = query.where(Room.floor == floor)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        query = select(func.count(Room.id))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_slots(self, room_id: int, date_in: date) -> list[dict]:
        slot_query = (
            select(Slot).where(Slot.room_id == room_id).order_by(Slot.start_time)
        )
        booking_query = (
            select(Booking)
            .where(
                Booking.room_id == room_id,
                func.date(Booking.start_time) == date_in,
            )
            .order_by(Booking.start_time)
        )
        slot_result = await self.session.execute(slot_query)
        booking_result = await self.session.execute(booking_query)

        slots = slot_result.scalars().all()
        bookings = booking_result.scalars().all()

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
