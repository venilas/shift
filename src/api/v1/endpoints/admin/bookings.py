from datetime import date

from fastapi import APIRouter, Body, Depends, Path, Query, status

from src.api.dependencies import get_booking_service, get_current_admin
from src.core.constants import (
    NOT_ADMIN_RESPONSE,
    NOT_FOUND_RESPONSES,
    UNAUTHORIZED_RESPONSE,
)
from src.models.user import User
from src.schemas.booking import (
    BookingAdminListResponse,
    BookingAdminResponse,
    BookingUpdate,
)
from src.services.booking import BookingService

router = APIRouter(
    prefix="/bookings",
    tags=["Admin Bookings"],
    dependencies=[Depends(get_current_admin)],
)


@router.get(
    "/",
    summary="Получение списка бронирований",
    description="""
Получения списка бронирований.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное получение списка бронирований",
            "content": {
                "application/json": {
                    "example": {
                        "bookings": {
                            "id": 1,
                            "user_id": 1,
                            "room_id": 1,
                            "start_time": date.today().strftime(
                                "%Y-%m-%dT10:00:00+03:00"
                            ),
                            "end_time": date.today().strftime(
                                "%Y-%m-%dT10:05:00+03:00"
                            ),
                            "description": "Room description",
                        }
                    },
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: {
            "description": "Комната/Пользователь не найден",
            "content": {
                "application/json": {
                    "examples": {
                        "room": {
                            "summary": "Комната не найдена",
                            "value": {
                                "detail": "Room not found",
                            },
                        },
                        "user": {
                            "summary": "Пользователь не найден",
                            "value": {
                                "detail": "User not found",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def get_bookings(
    room_id: int = Query(default=None, description="ID комнаты"),
    user_id: int = Query(default=None, description="ID пользователя"),
    date_in: date = Query(default=None, description="Дата в формате ISO (YYYY-MM-DD)"),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingAdminListResponse:
    bookings = await booking_service.get_bookings_admin(room_id, user_id, date_in)
    return BookingAdminListResponse(bookings=bookings)


@router.patch(
    "/{booking_id}",
    summary="Редактирование бронирования",
    description="""
Редактирование бронирования по ID.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное редактирование бронирования",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": 1,
                        "room_id": 1,
                        "start_time": date.today().strftime("%Y-%m-%dT10:00:00+03:00"),
                        "end_time": date.today().strftime("%Y-%m-%dT10:05:00+03:00"),
                        "description": "Room description",
                    },
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
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
    booking_id: int = Path(..., description="ID бронирования"),
    booking_in: BookingUpdate = Body(
        ...,
        examples=[
            {
                "room_id": 1,
                "user_id": 1,
                "start_time": date.today().strftime("%Y-%m-%d 10:00"),
                "end_time": date.today().strftime("%Y-%m-%d 10:05"),
                "description": "Room description",
            }
        ],
    ),
    current_admin: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingAdminResponse:
    return await booking_service.update_booking_admin(
        booking_id,
        booking_in,
        current_admin,
    )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление бронирования",
    description="""
Удаление бронирования по ID.

Требуется роль: Admin
""",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["booking_not_found"],
    },
)
async def delete_booking(
    booking_id: int = Path(..., description="ID бронирования"),
    current_admin: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service),
):
    await booking_service.delete_booking(booking_id, current_admin)
