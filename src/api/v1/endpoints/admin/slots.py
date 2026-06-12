from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin, get_room_service, get_slot_service
from src.models.user import User
from src.schemas.slot import SlotCreate, SlotResponse, SlotUpdate
from src.services.room import RoomService
from src.services.slot import SlotService

router = APIRouter(prefix="/slots", tags=["Admin Slots"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_slot(
    slot_in: SlotCreate,
    current_admin: User = Depends(get_current_admin),
    slot_service: SlotService = Depends(get_slot_service),
    room_serive: RoomService = Depends(get_room_service),
) -> SlotResponse:
    await room_serive.get_room_by_id(slot_in.room_id)

    return await slot_service.create_slot(slot_in)


@router.patch("/{slot_id}")
async def update_slot(
    slot_id: int,
    slot_in: SlotUpdate,
    current_admin: User = Depends(get_current_admin),
    slot_service: SlotService = Depends(get_slot_service),
    room_service: RoomService = Depends(get_room_service),
) -> SlotResponse:
    if slot_in.room_id:
        await room_service.get_room_by_id(slot_in.room_id)

    return await slot_service.update_slot(slot_id, slot_in)


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: int,
    current_admin: User = Depends(get_current_admin),
    slot_service: SlotService = Depends(get_slot_service),
):
    return await slot_service.delete_slot(slot_id)
