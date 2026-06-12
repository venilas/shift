from src.core.exceptions.slot import (
    BookingsOutsideNewSlotException,
    SlotNotAvailableException,
    SlotNotFoundException,
)
from src.db.repositories.slot import SlotRepository
from src.schemas.slot import SlotCreate, SlotResponse, SlotUpdate


class SlotService:
    def __init__(self, slot_repo: SlotRepository):
        self.slot_repo = slot_repo

    async def create_slot(self, slot_in: SlotCreate) -> SlotResponse:
        if not await self.slot_repo.is_slot_available(
            slot_in.room_id,
            slot_in.start_time,
            slot_in.end_time,
        ):
            raise SlotNotAvailableException()

        slot = await self.slot_repo.create(slot_in.model_dump())
        return SlotResponse.model_validate(slot)

    async def update_slot(self, slot_id: int, slot_in: SlotUpdate) -> SlotResponse:
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
            raise SlotNotAvailableException()

        if not await self.slot_repo.is_bookings_available(
            room_id,
            start_time,
            end_time,
        ):
            raise BookingsOutsideNewSlotException()

        slot = await self.slot_repo.update(slot_id, updated_data)
        return SlotResponse.model_validate(slot)

    async def delete_slot(self, slot_id: int) -> None:
        slot = await self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise SlotNotFoundException()

        await self.slot_repo.delete(slot_id)
