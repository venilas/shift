from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room


class RoomFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        title: str = "Test Room 1",
        floor: int = 1,
    ) -> Room:
        room = Room(
            title=title,
            floor=floor,
        )
        session.add(room)
        await session.flush()
        await session.refresh(room)

        return room
