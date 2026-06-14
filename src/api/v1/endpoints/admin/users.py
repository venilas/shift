from fastapi import APIRouter, Depends, Path, status

from src.api.dependencies import get_current_admin, get_user_service
from src.core.constants import (
    NOT_ADMIN_RESPONSE,
    NOT_FOUND_RESPONSES,
    UNAUTHORIZED_RESPONSE,
)
from src.schemas.user import UserResponse
from src.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Admin Users"],
    dependencies=[Depends(get_current_admin)],
)


@router.get(
    "/{user_id}",
    summary="Получение пользователя",
    description="""
Получение пользователя по ID.

Требуется роль: Admin
""",
    responses={
        200: {
            "description": "Успешное получение пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "login": "ivan_login",
                        "first_name": "Ivan",
                        "last_name": "Ivanov",
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["user_not_found"],
    },
)
async def get_user(
    user_id: int = Path(
        ...,
        description="ID пользователя",
    ),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_service.get_user_by_id(user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
    description="""
Удаление пользователя по ID.

Требуется роль: Admin
""",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: NOT_ADMIN_RESPONSE,
        404: NOT_FOUND_RESPONSES["user_not_found"],
    },
)
async def delete_user(
    user_id: int = Path(
        ...,
        description="ID пользователя",
    ),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(user_id)
