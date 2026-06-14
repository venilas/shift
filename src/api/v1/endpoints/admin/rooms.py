from fastapi import APIRouter, Body, Depends, Path, status

from src.api.dependencies import get_current_admin, get_room_service
from src.core.constants import (
    NOT_ADMIN_RESPONSE,
    NOT_FOUND_RESPONSES,
    UNAUTHORIZED_RESPONSE,
)
from src.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from src.services.room import RoomService

router = APIRouter(
    prefix="/rooms",
    tags=["Admin Rooms"],
    dependencies=[Depends(get_current_admin)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание комнаты",
    description="""
Создание комнаты.

Требуется роль: Admin
""",
    responses={
        201: {
            "description": "Успешное создание комнаты",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Room title",
                        "floor": 1,
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
    },
)
async def create_room(
    room_in: RoomCreate = Body(
        ...,
        examples=[
            {
                "title": "Room title",
                "floor": 1,
            }
        ],
    ),
    room_service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    return await room_service.create_room(room_in)


@router.patch(
    "/{room_id}",
    summary="Редактирование комнаты",
    description="""
Редактирование комнаты по ID.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное редактирование комнаты",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Room title",
                        "floor": 1,
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
    },
)
async def update_room(
    room_id: int = Path(..., description="ID комнаты"),
    room_in: RoomUpdate = Body(
        ...,
        examples=[
            {
                "title": "Room title",
                "floor": 1,
            }
        ],
    ),
    room_service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    return await room_service.update_room(room_id, room_in)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление комнаты",
    description="""
Удаление комнаты по ID.

Требуется роль: Admin
""",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
    },
)
async def delete_room(
    room_id: int = Path(..., description="ID комнаты"),
    room_service: RoomService = Depends(get_room_service),
):
    return await room_service.delete_room(room_id)
