from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin, get_room_service
from src.models.user import User
from src.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from src.services.room import RoomService

router = APIRouter(prefix="/rooms", tags=["Admin Rooms"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    current_admin: User = Depends(get_current_admin),
    room_service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    return await room_service.create_room(room_in)


@router.patch("/{room_id}")
async def update_room(
    room_id: int,
    room_in: RoomUpdate,
    current_admin: User = Depends(get_current_admin),
    room_service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    return await room_service.update_room(room_id, room_in)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    current_admin: User = Depends(get_current_admin),
    room_service: RoomService = Depends(get_room_service),
):
    return await room_service.delete_room(room_id)
