from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.slot import Slot


class SlotFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        room_id: int,
        start_time: time | None = None,
        end_time: time | None = None,
    ) -> Slot:
        if start_time is None:
            start_time = time(hour=8, minute=0)
        if end_time is None:
            end_time = time(hour=12, minute=0)

        slot = Slot(
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
        )
        session.add(slot)
        await session.flush()
        await session.refresh(slot)

        return slot
