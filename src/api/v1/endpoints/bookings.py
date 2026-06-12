from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_booking_service, get_current_user, get_room_service
from src.models.user import User
from src.schemas.booking import (
    BookingCreate,
    BookingListResponse,
    BookingResponse,
    BookingUpdate,
)
from src.services.booking import BookingService
from src.services.room import RoomService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
) -> BookingResponse:
    await room_service.get_room_by_id(booking_in.room_id)

    return await booking_service.create(booking_in, current_user)


@router.get("/")
async def get_bookings(
    room_id: int = Query(default=None),
    date: datetime = Query(default=None),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingListResponse:
    bookings = await booking_service.get_bookings(room_id, current_user.id, date)
    return BookingListResponse(bookings=bookings)


@router.patch("/{booking_id}")
async def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
) -> BookingResponse:
    if booking_in.room_id:
        await room_service.get_room_by_id(booking_in.room_id)

    return await booking_service.update(booking_id, booking_in, current_user)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    await booking_service.delete(booking_id, current_user)
