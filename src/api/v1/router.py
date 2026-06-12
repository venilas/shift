from fastapi import APIRouter

from src.api.v1.endpoints import auth, bookings, rooms
from src.api.v1.endpoints import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(rooms.router)
router.include_router(bookings.router)
router.include_router(admin_router.router)
