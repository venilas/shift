from fastapi import APIRouter

from src.api.v1.endpoints.admin import bookings, rooms, slots, users

router = APIRouter(prefix="/admin")

router.include_router(rooms.router)
router.include_router(bookings.router)
router.include_router(slots.router)
router.include_router(users.router)
