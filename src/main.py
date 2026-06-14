from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import router
from src.config.settings import get_settings
from src.core.exceptions.base import MyBaseException
from src.middleware.error_handler import general_exception_handler, my_exception_handler

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")


tags_metadata = [
    {
        "name": "Authentication",
        "description": "Регистрация и авторизация пользователей",
    },
    {
        "name": "Rooms",
        "description": "Работа с комнатами",
    },
    {
        "name": "Bookings",
        "description": "Создание и управление бронированиями",
    },
    {
        "name": "Admin Slots",
        "description": "Методы администратора для управления слотами комнаты",
    },
    {
        "name": "Admin Rooms",
        "description": "Методы администратора для управления комнатами",
    },
    {
        "name": "Admin Bookings",
        "description": "Методы администратора для управления бронированиями",
    },
    {
        "name": "Admin Users",
        "description": "Методы администратора для управления пользователями",
    },
]

app = FastAPI(
    version="1.0.0",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
    description="""
## Authentication

Используйте Bearer Token:

Authorization: Bearer `<token>`

---

## Роли

- User
- Admin
    """,
    contact={
        "name": "Ilyas Aminev",
        "email": "ilyasaminev3@mail.ru",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in get_settings().BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(MyBaseException, my_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(router, prefix="/api")
