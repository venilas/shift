from fastapi import APIRouter, Body, Depends, status

from src.api.dependencies import get_auth_service
from src.schemas.auth import LoginRequest, Token
from src.schemas.user import UserCreate
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация",
    description="Регистрация пользователя",
    responses={
        201: {
            "description": "Успешная регистрация",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhb...",
                        "token_type": "Bearer",
                    }
                }
            },
        },
        409: {
            "description": "Логин уже занят",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Login already registered",
                    }
                }
            },
        },
    },
)
async def register(
    user_in: UserCreate = Body(
        examples=[
            {
                "login": "ivan_login",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "password": "ivan_password",
            }
        ]
    ),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.register(user_in)


@router.post(
    "/login",
    summary="Авторизация",
    description="Авторизация пользователя",
    responses={
        200: {
            "description": "Успешная авторизация",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhb...",
                        "token_type": "Bearer",
                    }
                }
            },
        },
        401: {
            "description": "Неверный логин или пароль",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect login or password",
                    }
                }
            },
        },
    },
)
async def login(
    login_data: LoginRequest = Body(
        examples=[
            {
                "login": "ivan_login",
                "password": "ivan_password",
            }
        ]
    ),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(login_data)
