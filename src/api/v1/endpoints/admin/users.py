from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin, get_user_service
from src.models.user import User
from src.schemas.user import UserResponse
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["Admin Users"])


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_service.get_user_by_id(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    cuurent_admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(user_id)
