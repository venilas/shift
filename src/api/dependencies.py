from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.user import ForbiddenException, InvalidTokenException
from src.core.security import security_service
from src.db.repositories.booking import BookingRepository
from src.db.repositories.room import RoomRepository
from src.db.repositories.slot import SlotRepository
from src.db.repositories.user import UserRepository
from src.db.session import get_db
from src.models.enums import UserRole
from src.models.user import User
from src.services.auth import AuthService
from src.services.booking import BookingService
from src.services.room import RoomService
from src.services.slot import SlotService
from src.services.user import UserService

security = HTTPBearer()


async def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    token = credentials.credentials
    payload = security_service.decode_token(token)

    if not payload or payload.get("type") != "access":
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    try:
        user = await user_repo.get_by_id(int(user_id))
    except ValueError:
        raise InvalidTokenException()

    if not user:
        raise InvalidTokenException()

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Forbidden")

    return current_user


async def get_room_repo(session: AsyncSession = Depends(get_db)) -> RoomRepository:
    return RoomRepository(session)


async def get_booking_repo(
    session: AsyncSession = Depends(get_db),
) -> BookingRepository:
    return BookingRepository(session)


async def get_slot_repo(session: AsyncSession = Depends(get_db)) -> SlotRepository:
    return SlotRepository(session)


async def get_room_service(
    room_repo: RoomRepository = Depends(get_room_repo),
    slot_repo: SlotRepository = Depends(get_slot_repo),
    booking_repo: BookingRepository = Depends(get_booking_repo),
) -> RoomService:
    return RoomService(
        room_repo=room_repo,
        slot_repo=slot_repo,
        booking_repo=booking_repo,
    )


async def get_booking_service(
    booking_repo: BookingRepository = Depends(get_booking_repo),
    room_repo: RoomRepository = Depends(get_room_repo),
    slot_repo: SlotRepository = Depends(get_slot_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> BookingService:
    return BookingService(
        booking_repo=booking_repo,
        room_repo=room_repo,
        slot_repo=slot_repo,
        user_repo=user_repo,
    )


async def get_slot_service(
    slot_repo: SlotRepository = Depends(get_slot_repo),
    room_repo: RoomRepository = Depends(get_room_repo),
    booking_repo: BookingRepository = Depends(get_booking_repo),
) -> SlotService:
    return SlotService(
        slot_repo=slot_repo,
        room_repo=room_repo,
        booking_repo=booking_repo,
    )
