from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_auth_service
from src.schemas.auth import LoginRequest, Token
from src.schemas.user import UserCreate
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.register(user_in)


@router.post("/login")
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(login_data)
