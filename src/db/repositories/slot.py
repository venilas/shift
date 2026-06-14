from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import Time, cast, delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.models.booking import Booking
from src.models.slot import Slot


class SlotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, slot_in: dict) -> Slot:
        slot = Slot(**slot_in)
        self.session.add(slot)
        await self.session.flush()
        await self.session.refresh(slot)
        return slot

    async def is_slot_available(
        self,
        room_id: int,
        start_time: time,
        end_time: time,
        without_slot_id: int | None = None,
    ) -> bool:
        """Нет ли пересечений с другими слотами"""

        stmt = exists().where(
            Slot.room_id == room_id,
            Slot.start_time < end_time,
            Slot.end_time > start_time,
        )

        if without_slot_id:
            stmt = stmt.where(Slot.id != without_slot_id)

        query = select(stmt)

        result = await self.session.execute(query)
        return not result.scalar()

    async def is_booking_available(
        self,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """Есть ли диапазон слотов, куда может поместиться бронь"""

        tz = ZoneInfo(key=get_settings().TIMEZONE)
        start_time = start_time.astimezone(tz=tz)
        end_time = end_time.astimezone(tz=tz)

        query = select(
            exists().where(
                Slot.room_id == room_id,
                Slot.start_time <= start_time.time(),
                Slot.end_time >= end_time.time(),
            )
        )

        result = await self.session.execute(query)
        return result.scalar() or False

    async def is_bookings_available(
        self,
        room_id: int,
        start_time: time,
        end_time: time,
    ) -> bool:
        """Нет ли бронирований вне диапозона слота"""

        query = select(
            exists().where(
                Booking.room_id == room_id,
                or_(
                    cast(Booking.start_time, Time) < start_time,
                    cast(Booking.end_time, Time) > end_time,
                ),
            )
        )
        result = await self.session.execute(query)
        return not result.scalar()

    async def get_by_id(self, slot_id: int) -> Slot | None:
        query = select(Slot).where(Slot.id == slot_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, room_id: int) -> list[Slot]:
        query = select(Slot).where(Slot.room_id == room_id).order_by(Slot.start_time)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, slot_id: int, slot_in: dict) -> Slot | None:
        slot = await self.get_by_id(slot_id)
        if not slot:
            return None

        for key, value in slot_in.items():
            if getattr(slot, key, None):
                setattr(slot, key, value)

        self.session.add(slot)
        await self.session.flush()
        return slot

    async def delete(self, slot_id: int) -> None:
        query = delete(Slot).where(Slot.id == slot_id)
        await self.session.execute(query)
