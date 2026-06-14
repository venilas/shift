from unittest.mock import AsyncMock

import pytest

from src.services.auth import AuthService
from src.services.booking import BookingService
from src.services.room import RoomService
from src.services.slot import SlotService
from src.services.user import UserService


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def room_repo():
    return AsyncMock()


@pytest.fixture
def slot_repo():
    return AsyncMock()


@pytest.fixture
def booking_repo():
    return AsyncMock()


@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo=user_repo)


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo=user_repo)


@pytest.fixture
def room_service(room_repo, slot_repo, booking_repo):
    return RoomService(
        room_repo=room_repo,
        slot_repo=slot_repo,
        booking_repo=booking_repo,
    )


@pytest.fixture
def slot_service(slot_repo, room_repo, booking_repo):
    return SlotService(
        slot_repo=slot_repo,
        room_repo=room_repo,
        booking_repo=booking_repo,
    )


@pytest.fixture
def booking_service(booking_repo, room_repo, slot_repo, user_repo):
    return BookingService(
        booking_repo=booking_repo,
        room_repo=room_repo,
        slot_repo=slot_repo,
        user_repo=user_repo,
    )
