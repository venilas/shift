from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_current_user, get_room_service
from src.config.settings import get_settings
from src.core.exceptions.common import DateInPastException
from src.models.user import User
from src.schemas.room import RoomListResponse
from src.schemas.slot import SlotListAvailability
from src.services.room import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/")
async def get_rooms(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    floor: int | None = Query(default=None),
    room_service: RoomService = Depends(get_room_service),
    current_user: User = Depends(get_current_user),
) -> RoomListResponse:
    offset = (page - 1) * page_size
    rooms, total = await room_service.get_rooms(offset, page_size, floor)

    return RoomListResponse(
        rooms=rooms,
        total=total,
        page=page,
        page_size=page_size,
        floor=floor,
    )


@router.get("/{room_id}/availability")
async def get_room_availability(
    room_id: int,
    date: date = Query(
        ...,
        description="Date in ISO format (YYYY-MM-DD)",
        examples=[date.today().strftime("%Y-%m-%d")],
        format="date",
    ),
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
) -> SlotListAvailability:
    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz).date()

    if date < today:
        raise DateInPastException()

    slots = await room_service.get_room_availability(room_id, date)
    return SlotListAvailability(slots=slots)
