from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.models.booking import Booking


class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, booking_in: dict) -> Booking:
        booking = Booking(**booking_in)
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def is_booking_available(
        self,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        without_booking_id: int | None = None,
    ) -> bool:
        """Нет ли пересечений с другими бронированиями"""

        stmt = exists().where(
            Booking.room_id == room_id,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )

        if without_booking_id:
            stmt = stmt.where(Booking.id != without_booking_id)

        query = select(stmt)

        result = await self.session.execute(query)
        return not result.scalar()

    async def get_by_id(self, booking_id: int) -> Booking | None:
        query = select(Booking).where(Booking.id == booking_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        room_id: int | None,
        user_id: int | None,
        date_in: date | None,
    ) -> list[Booking]:
        query = select(Booking).order_by(Booking.start_time)

        if room_id:
            query = query.where(Booking.room_id == room_id)

        if user_id:
            query = query.where(Booking.user_id == user_id)

        if date_in:
            query = query.where(func.date(Booking.end_time) >= date_in)
        else:
            tz = ZoneInfo(key=get_settings().TIMEZONE)
            today = datetime.now(tz=tz).date()

            query = query.where(func.date(Booking.end_time) == today)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, booking_id: int, booking_in: dict) -> Booking | None:
        booking = await self.get_by_id(booking_id)
        if not booking:
            return None

        for key, value in booking_in.items():
            if getattr(booking, key, None):
                setattr(booking, key, value)

        self.session.add(booking)
        await self.session.flush()
        return booking

    async def delete(self, booking_id: int) -> None:
        query = delete(Booking).where(Booking.id == booking_id)
        await self.session.execute(query)
        await self.session.commit()
