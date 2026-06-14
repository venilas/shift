from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room


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

    async def get_multi(self, offset: int, limit: int, floor: int | None) -> list[Room]:
        query = select(Room).offset(offset).limit(limit).order_by(Room.id)
        if floor:
            query = query.where(Room.floor == floor)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        query = select(func.count(Room.id))
        result = await self.session.execute(query)
        return result.scalar() or 0

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
