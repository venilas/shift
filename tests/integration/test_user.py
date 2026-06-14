import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import UserRole

from .api.booking import BookingAPI
from .api.user import UserAPI
from .factories.base import BaseFactory
from .factories.booking import BookingFactory
from .factories.room import RoomFactory
from .factories.slot import SlotFactory
from .factories.user import UserFactory


@pytest.mark.asyncio
async def test_get_user_admin(
    client: AsyncClient,
    auth_data_admin: dict,
    auth_data_user: dict,
):
    user_api = UserAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    response = await user_api.get(auth_data_admin, user_id)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "id": user_id,
        "first_name": "Ilyas",
        "last_name": "Aminev",
        "login": "venilo_o",
    }


@pytest.mark.asyncio
async def test_delete_user_admin(
    client: AsyncClient,
    auth_data_admin: dict,
    auth_data_user: dict,
):
    user_api = UserAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    response = await user_api.delete(auth_data_admin, user_id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_bookings_user(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_api = UserAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    response = await booking_api.get_multi(auth_data_admin, date_in=msc_datetime.date())
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "bookings": [
            {
                "id": booking.id,
                "user_id": user_id,
                "room_id": room.id,
                "start_time": BaseFactory._response_strftime_time(booking.start_time),
                "end_time": BaseFactory._response_strftime_time(booking.end_time),
                "description": "Test Description",
            }
        ]
    }

    response = await user_api.delete(auth_data_admin, user_id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await booking_api.get_multi(auth_data_admin, date_in=msc_datetime.date())
    data = response.json()

    assert data == {"bookings": []}


@pytest.mark.asyncio
async def test_get_user_admin_invalid_user(client: AsyncClient, auth_data_admin: dict):
    user_api = UserAPI(client)

    response = await user_api.get(auth_data_admin, user_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_admin_invalid_user(
    client: AsyncClient,
    auth_data_admin: dict,
):
    user_api = UserAPI(client)

    response = await user_api.delete(auth_data_admin, user_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_other_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    user_api = UserAPI(client)

    user = await UserFactory.create(db_session, login="venilo_o", role=UserRole.ADMIN)

    response = await user_api.delete(auth_data_admin, user.id)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden delete an admin"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, auth_data_user: dict):
    user_api = UserAPI(client)

    response = await user_api.delete(auth_data_user, user_id=1)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"
