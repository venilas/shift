from datetime import date

from src.core.exceptions.room import RoomNotFoundException
from src.db.repositories.room import RoomRepository
from src.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from src.schemas.slot import SlotAvailability


class RoomService:
    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    async def create_room(self, room_in: RoomCreate) -> RoomResponse:
        room = await self.room_repo.create(room_in.model_dump())
        return RoomResponse.model_validate(room)

    async def update_room(self, room_id: int, room_in: RoomUpdate) -> RoomResponse:
        update_data = room_in.model_dump(exclude_unset=True)

        await self.get_room_by_id(room_id)

        room = await self.room_repo.update(room_id, update_data)
        return RoomResponse.model_validate(room)

    async def delete_room(self, room_id: int) -> None:
        await self.get_room_by_id(room_id)
        await self.room_repo.delete(room_id)

    async def get_rooms(
        self,
        offset: int,
        limit: int,
        floor: int | None,
    ) -> tuple[list[RoomResponse], int]:
        rooms_in_db = await self.room_repo.get_rooms(offset, limit, floor)
        rooms: list[RoomResponse] = [
            RoomResponse.model_validate(room) for room in rooms_in_db
        ]
        total = await self.room_repo.count()
        return rooms, total

    async def get_room_availability(
        self,
        room_id: int,
        date_in: date,
    ) -> list[SlotAvailability]:
        await self.get_room_by_id(room_id)

        slots = await self.room_repo.get_slots(room_id, date_in)
        return [SlotAvailability(**slot) for slot in slots]

    async def get_room_by_id(self, room_id: int) -> RoomResponse:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException()
        return RoomResponse.model_validate(room)
