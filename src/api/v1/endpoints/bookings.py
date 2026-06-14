from datetime import date

from fastapi import APIRouter, Body, Depends, Path, Query, status

from src.api.dependencies import get_booking_service, get_current_user
from src.core.constants import NOT_FOUND_RESPONSES, UNAUTHORIZED_RESPONSE
from src.models.user import User
from src.schemas.booking import (
    BookingCreate,
    BookingListResponse,
    BookingResponse,
    BookingUpdate,
)
from src.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание бронирования",
    description="Создание бронирования",
    responses={
        201: {
            "description": "Успешное создание",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "room_id": 1,
                        "start_time": date.today().strftime("%Y-%m-%dT10:00:00+03:00"),
                        "end_time": date.today().strftime("%Y-%m-%dT10:05:00+03:00"),
                        "description": "Room description",
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
        409: {
            "description": "Конфликт бронирования",
            "content": {
                "application/json": {
                    "examples": {
                        "outside_slot": {
                            "summary": "Вне доступного слота",
                            "value": {
                                "detail": "Booking must be inside room slot",
                            },
                        },
                        "booking_overlap": {
                            "summary": "Пересечение бронирований",
                            "value": {
                                "detail": "Booking overlaps with another booking",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def create_booking(
    booking_in: BookingCreate = Body(
        ...,
        examples=[
            {
                "room_id": 1,
                "start_time": date.today().strftime("%Y-%m-%d 10:00"),
                "end_time": date.today().strftime("%Y-%m-%d 10:05"),
                "description": "Room description",
            },
        ],
    ),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    return await booking_service.create_booking(booking_in, current_user)


@router.get(
    "/",
    summary="Список своих бронирований",
    description="Получение списка своих бронирований",
    responses={
        200: {
            "description": "Успешное получение списка своих бронирований",
            "content": {
                "application/json": {
                    "example": {
                        "bookings": [
                            {
                                "id": 1,
                                "room_id": 1,
                                "start_time": date.today().strftime(
                                    "%Y-%m-%dT10:00:00+03:00"
                                ),
                                "end_time": date.today().strftime(
                                    "%Y-%m-%dT10:05:00+03:00"
                                ),
                                "description": "Room description",
                            },
                        ]
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
    },
)
async def get_bookings(
    room_id: int | None = Query(
        default=None,
        description="ID комнаты",
    ),
    date_in: date | None = Query(
        default=None,
        description="Дата в формате ISO (YYYY-MM-DD)",
    ),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingListResponse:
    bookings = await booking_service.get_bookings(room_id, current_user.id, date_in)
    return BookingListResponse(bookings=bookings)


@router.patch(
    "/{booking_id}",
    summary="Редактирование бронирования",
    description="Редактироние своего бронирования по ID",
    responses={
        200: {
            "description": "Успешное редактирование своего бронирования",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "room_id": 1,
                        "start_time": date.today().strftime("%Y-%m-%dT10:00:00+03:00"),
                        "end_time": date.today().strftime("%Y-%m-%dT10:05:00+03:00"),
                        "description": "Room description",
                    },
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: {
            "description": "Редактирование чужого бронирования",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not permission to update this booking",
                    }
                }
            },
        },
        404: {
            "description": "Комната/Бронирование не найдено",
            "content": {
                "application/json": {
                    "examples": {
                        "booking": {
                            "summary": "Бронирование не найдено",
                            "value": {"detail": "Booking not found"},
                        },
                        "room": {
                            "summary": "Комната не найдена",
                            "value": {"detail": "Room not found"},
                        },
                    }
                }
            },
        },
        409: {
            "description": "Конфликт бронирования",
            "content": {
                "application/json": {
                    "examples": {
                        "outside_slot": {
                            "summary": "Вне доступного слота",
                            "value": {
                                "detail": "Booking must be inside room slot",
                            },
                        },
                        "booking_overlap": {
                            "summary": "Пересечение бронирований",
                            "value": {
                                "detail": "Booking overlaps with another booking",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_booking(
    booking_id: int = Path(
        ...,
        description="ID бронирования",
    ),
    booking_in: BookingUpdate = Body(
        ...,
        examples=[
            {
                "room_id": 1,
                "start_time": date.today().strftime("%Y-%m-%d 10:00"),
                "end_time": date.today().strftime("%Y-%m-%d 10:05"),
                "description": "Room description",
            },
        ],
    ),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    return await booking_service.update_booking(booking_id, booking_in, current_user)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление бронирования",
    description="Удаление своего бронирования по ID",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: {
            "description": "Удаление чужого бронирования",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not permission to delete this booking",
                    }
                }
            },
        },
        404: NOT_FOUND_RESPONSES["booking_not_found"],
    },
)
async def delete_booking(
    booking_id: int = Path(
        ...,
        description="ID бронирования",
    ),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    await booking_service.delete_booking(booking_id, current_user)
