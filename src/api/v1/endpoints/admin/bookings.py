from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import (
    get_booking_service,
    get_current_admin,
    get_room_service,
    get_user_service,
)
from src.config.settings import get_settings
from src.models.user import User
from src.schemas.booking import BookingListResponse, BookingResponse, BookingUpdate
from src.services.booking import BookingService
from src.services.room import RoomService
from src.services.user import UserService

router = APIRouter(prefix="/bookings", tags=["Admin Bookings"])


@router.get("/")
async def get_bookings(
    room_id: int = Query(default=None),
    user_id: int = Query(default=None),
    date: datetime = Query(default=None),
    current_admin: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
    user_service: UserService = Depends(get_user_service),
) -> BookingListResponse:
    tz = ZoneInfo(key=get_settings().TIMEZONE)
    if date:
        date = date.replace(tzinfo=tz)

    if room_id:
        await room_service.get_room_by_id(room_id)

    if user_id:
        await user_service.get_user_by_id(user_id)

    bookings = await booking_service.get_bookings(room_id, user_id, date)
    return BookingListResponse(bookings=bookings)


@router.patch("/{booking_id}")
async def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    current_admin: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
) -> BookingResponse:
    if booking_in.room_id:
        await room_service.get_room_by_id(booking_in.room_id)

    return await booking_service.update(booking_id, booking_in, current_admin)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    current_admin: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service),
):
    await booking_service.delete(booking_id, current_admin)
