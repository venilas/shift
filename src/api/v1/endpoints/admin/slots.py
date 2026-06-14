from fastapi import APIRouter, Body, Depends, Path, status

from src.api.dependencies import get_current_admin, get_slot_service
from src.core.constants import (
    NOT_ADMIN_RESPONSE,
    NOT_FOUND_RESPONSES,
    UNAUTHORIZED_RESPONSE,
)
from src.schemas.slot import SlotCreate, SlotListResponse, SlotResponse, SlotUpdate
from src.services.slot import SlotService

router = APIRouter(
    prefix="/slots",
    tags=["Admin Slots"],
    dependencies=[Depends(get_current_admin)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание слота",
    description="""
Создание слота.

Требуется роль: Admin
""",
    responses={
        201: {
            "description": "Успешное создание слота",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "room_id": 1,
                        "start_time": "08:00",
                        "end_time": "12:00",
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
        409: {
            "description": "Слот пересекается с другим слотом",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Slot overlaps with another slot",
                    }
                }
            },
        },
    },
)
async def create_slot(
    slot_in: SlotCreate = Body(
        ...,
        examples=[
            {
                "room_id": 1,
                "start_time": "08:00",
                "end_time": "12:00",
            }
        ],
    ),
    slot_service: SlotService = Depends(get_slot_service),
) -> SlotResponse:
    return await slot_service.create_slot(slot_in)


@router.get(
    "/{room_id}",
    summary="Получение слотов комнаты",
    description="""
Получение слотов комнаты по ID.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное создание слота",
            "content": {
                "application/json": {
                    "example": {
                        "slots": [
                            {
                                "id": 1,
                                "room_id": 1,
                                "start_time": "08:00:00",
                                "end_time": "12:00:00",
                            }
                        ]
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["room_not_found"],
    },
)
async def get_slots(
    room_id: int = Path(
        ...,
        description="ID комнаты",
    ),
    slot_service: SlotService = Depends(get_slot_service),
) -> SlotListResponse:
    slots = await slot_service.get_slots(room_id)
    return SlotListResponse(slots=slots)


@router.patch(
    "/{slot_id}",
    summary="Редактирование слота",
    description="""
Редактирование слота по ID.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное редактирование слота",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "room_id": 1,
                        "start_time": "08:00",
                        "end_time": "12:00",
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: {
            "description": "Слот/Комната не найдена",
            "content": {
                "application/json": {
                    "examples": {
                        "room": {
                            "summary": "Комната не найдена",
                            "value": {
                                "detail": "Room not found",
                            },
                        },
                        "slot": {
                            "summary": "Слот не найден",
                            "value": {
                                "detail": "Slot not found",
                            },
                        },
                    }
                }
            },
        },
        409: {
            "description": "Конфликты",
            "content": {
                "application/json": {
                    "examples": {
                        "slot": {
                            "summary": "Слот пересекается с другим слотом",
                            "value": {
                                "detail": "Slot overlaps with another slot",
                            },
                        },
                        "booking": {
                            "summary": "Есть бронирования вне нового слота",
                            "value": {
                                "detail": "Slot cannot be updated because existing bookings would be outside new range"
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_slot(
    slot_id: int = Path(
        ...,
        description="ID слота",
    ),
    slot_in: SlotUpdate = Body(
        ...,
        examples=[
            {
                "room_id": 1,
                "start_time": "08:00",
                "end_time": "10:00",
            }
        ],
    ),
    slot_service: SlotService = Depends(get_slot_service),
) -> SlotResponse:
    return await slot_service.update_slot(slot_id, slot_in)


@router.delete(
    "/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление слота",
    description="""
Удаление слота по ID.

Требуется роль: Admin
""",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["slot_not_found"],
    },
)
async def delete_slot(
    slot_id: int = Path(
        ...,
        description="ID слота",
    ),
    slot_service: SlotService = Depends(get_slot_service),
):
    return await slot_service.delete_slot(slot_id)
