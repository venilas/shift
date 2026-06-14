from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Path, Query

from src.api.dependencies import get_current_user, get_room_service
from src.config.settings import get_settings
from src.core.constants import NOT_FOUND_RESPONSES, UNAUTHORIZED_RESPONSE
from src.core.exceptions.common import DateInPastException
from src.schemas.room import RoomListResponse
from src.schemas.slot import SlotListAvailability
from src.services.room import RoomService

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Список комнат",
    description="Получение списка комнат",
    responses={
        200: {
            "description": "Успешное получение списка комнат",
            "content": {
                "application/json": {
                    "example": {
                        "rooms": {
                            "id": 1,
                            "title": "Room title",
                            "floor": 1,
                        },
                        "total": 1,
                        "page": 1,
                        "page_size": 10,
                        "floor": None,
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
    },
)
async def get_rooms(
    page: int = Query(
        default=1,
        ge=1,
        description="Номер страницы",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Количество комнат на странице",
    ),
    floor: int | None = Query(
        default=None,
        description="Этаж",
    ),
    room_service: RoomService = Depends(get_room_service),
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


@router.get(
    "/{room_id}/availability",
    summary="Доступные слоты комнаты",
    description="Получение доступных слотов комнаты для бронирования",
    responses={
        200: {
            "description": "Успешное получение доступных слотов комнаты для бронирования",
            "content": {
                "application/json": {
                    "example": {
                        "slots": [
                            {
                                "start_time": "08:00:00",
                                "end_time": "12:00:00",
                            }
                        ]
                    }
                }
            },
        },
        400: {
            "description": "Указана прошлая дата",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Date in the past",
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
    },
)
async def get_room_availability(
    room_id: int = Path(
        ...,
        description="ID комнаты",
    ),
    date_in: date = Query(
        ...,
        description="Дата в формате ISO (YYYY-MM-DD)",
        examples=[date.today().strftime("%Y-%m-%d")],
        format="date",
    ),
    room_service: RoomService = Depends(get_room_service),
) -> SlotListAvailability:
    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz).date()

    if date_in < today:
        raise DateInPastException()

    slots = await room_service.get_room_availability(room_id, date_in)
    return SlotListAvailability(slots=slots)
