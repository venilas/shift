from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.models.booking import Booking


class BookingFactory:
    @staticmethod
    def _get_msc_date() -> datetime:
        tz = ZoneInfo(key=get_settings().TIMEZONE)
        return datetime.now(tz=tz)

    @staticmethod
    def _get_time(old_date: datetime, hour: int, minute: int) -> datetime:
        return old_date.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: int,
        room_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        description: str | None = "Test Description",
    ) -> Booking:
        date = BookingFactory._get_msc_date()
        if start_time is None:
            start_time = BookingFactory._get_time(date, 8, 0)
        if end_time is None:
            end_time = BookingFactory._get_time(date, 8, 10)

        booking = Booking(
            user_id=user_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            description=description,
        )
        session.add(booking)
        await session.flush()
        await session.refresh(booking)

        return booking
