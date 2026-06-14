from src.core.exceptions.slot import (
    SlotContainsBookingsException,
    SlotNotFoundException,
    SlotOverlapException,
)
from src.db.repositories.booking import BookingRepository
from src.db.repositories.room import RoomRepository
from src.db.repositories.slot import SlotRepository
from src.schemas.slot import SlotCreate, SlotResponse, SlotUpdate
from src.services.room import RoomService


class SlotService:
    def __init__(
        self,
        slot_repo: SlotRepository,
        room_repo: RoomRepository,
        booking_repo: BookingRepository,
    ):
        self.slot_repo = slot_repo
        self.room_repo = room_repo
        self.booking_repo = booking_repo

    async def create_slot(self, slot_in: SlotCreate) -> SlotResponse:
        room_service = RoomService(
            room_repo=self.room_repo,
            slot_repo=self.slot_repo,
            booking_repo=self.booking_repo,
        )
        await room_service.get_room_by_id(slot_in.room_id)

        if not await self.slot_repo.is_slot_available(
            slot_in.room_id,
            slot_in.start_time,
            slot_in.end_time,
        ):
            raise SlotOverlapException()

        slot = await self.slot_repo.create(slot_in.model_dump())
        return SlotResponse.model_validate(slot)

    async def get_slots(self, room_id: int) -> list[SlotResponse]:
        room_service = RoomService(
            room_repo=self.room_repo,
            slot_repo=self.slot_repo,
            booking_repo=self.booking_repo,
        )
        await room_service.get_room_by_id(room_id)

        slots = await self.slot_repo.get_multi(room_id)
        return [SlotResponse.model_validate(slot) for slot in slots]

    async def update_slot(self, slot_id: int, slot_in: SlotUpdate) -> SlotResponse:
        if slot_in.room_id:
            room_service = RoomService(
                room_repo=self.room_repo,
                slot_repo=self.slot_repo,
                booking_repo=self.booking_repo,
            )
            await room_service.get_room_by_id(slot_in.room_id)

        slot = await self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise SlotNotFoundException()

        updated_data = slot_in.model_dump(exclude_unset=True)

        room_id = slot_in.room_id or slot.room_id
        start_time = slot_in.start_time or slot.start_time
        end_time = slot_in.end_time or slot.end_time

        slot_in.start_time = start_time
        slot_in.end_time = end_time
        slot_in = slot_in.model_validate(slot_in.model_dump())

        if not await self.slot_repo.is_slot_available(
            room_id,
            start_time,
            end_time,
            without_slot_id=slot_id,
        ):
            raise SlotOverlapException()

        if not await self.slot_repo.is_bookings_available(
            room_id,
            start_time,
            end_time,
        ):
            raise SlotContainsBookingsException()

        slot = await self.slot_repo.update(slot_id, updated_data)
        return SlotResponse.model_validate(slot)

    async def delete_slot(self, slot_id: int) -> None:
        slot = await self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise SlotNotFoundException()

        await self.slot_repo.delete(slot_id)
