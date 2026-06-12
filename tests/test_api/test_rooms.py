import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import UserRole

from .api.auth import AuthAPI
from .api.booking import BookingAPI
from .api.room import RoomAPI
from .factories.base import BaseFactory
from .factories.room import RoomFactory
from .factories.slot import SlotFactory
from .factories.user import UserFactory


@pytest.mark.asyncio
async def test_create_room_admin(client: AsyncClient, auth_data_admin: dict):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_admin)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data == {"id": data["id"], "floor": 1, "title": "Test Room 1"}


@pytest.mark.asyncio
async def test_update_room_admin(client: AsyncClient, auth_data_admin: dict):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_admin)
    data = response.json()
    room_id = data["id"]

    response = await room_api.update(
        auth_data_admin,
        room_id=room_id,
        title="Test Room 1 (Rename)",
        floor=2,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"id": room_id, "floor": 2, "title": "Test Room 1 (Rename)"}


@pytest.mark.asyncio
async def test_delete_room_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.delete(auth_data_admin, room_id=room.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_rooms(client: AsyncClient, auth_data_user: dict):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(auth_data_user)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"page": 1, "page_size": 10, "rooms": [], "total": 0, "floor": None}


@pytest.mark.asyncio
async def test_get_rooms_set_params(client: AsyncClient, auth_data_user: dict):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(
        auth_data_user,
        page=2,
        page_size=5,
        floor=2,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"page": 2, "page_size": 5, "rooms": [], "total": 0, "floor": 2}


@pytest.mark.asyncio
async def test_get_room_availability(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.get_availability(auth_data_user, room.id)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"slots": []}


@pytest.mark.asyncio
async def test_create_room_admin_short_title(
    client: AsyncClient,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_admin, title="")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 1 character"


@pytest.mark.asyncio
async def test_create_room_admin_long_title(client: AsyncClient, auth_data_admin: dict):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_admin, title="R" * 101)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 100 characters"


@pytest.mark.asyncio
async def test_create_room_admin_invalid_floor(
    client: AsyncClient,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_admin, floor="one")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.asyncio
async def test_update_room_admin_short_title(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.update(auth_data_admin, room_id=room.id, title="")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 1 character"


@pytest.mark.asyncio
async def test_update_room_admin_long_title(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.update(auth_data_admin, room_id=room.id, title="R" * 101)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 100 characters"


@pytest.mark.asyncio
async def test_update_room_admin_invalid_floor(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.update(auth_data_admin, room_id=room.id, floor="one")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.asyncio
async def test_update_room_admin_invalid_room_id(
    client: AsyncClient,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.update(
        auth_data_admin,
        room_id=1_000,
        title="Test Room 1 (Rename)",
    )
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room is not found"


@pytest.mark.asyncio
async def test_delete_room_admin_invalid_room_id(
    client: AsyncClient,
    auth_data_admin: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.delete(auth_data_admin, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room is not found"


@pytest.mark.asyncio
async def test_get_rooms_unauthorized(client: AsyncClient):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(auth_data=None)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_room_not_admin(client: AsyncClient, auth_data_user: dict):
    room_api = RoomAPI(client)

    response = await room_api.create(auth_data_user)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_get_rooms_invalid_short_page(client: AsyncClient, auth_data_user: dict):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(auth_data_user, page=-1)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "Input should be greater than or equal to 1"


@pytest.mark.asyncio
async def test_get_rooms_invalid_short_page_size(
    client: AsyncClient,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(auth_data_user, page_size=-1)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "Input should be greater than or equal to 1"


@pytest.mark.asyncio
async def test_get_rooms_invalid_long_page_size(
    client: AsyncClient,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.get_multi(auth_data_user, page_size=1_000)

    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "Input should be less than or equal to 50"


@pytest.mark.asyncio
async def test_get_rooms_after_filling(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.get_multi(auth_data_user)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "page": 1,
        "page_size": 10,
        "rooms": [
            {
                "id": room.id,
                "title": room.title,
                "floor": room.floor,
            }
        ],
        "total": 1,
        "floor": None,
    }

    response = await room_api.get_multi(auth_data_user, page=2)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"page": 2, "page_size": 10, "rooms": [], "total": 1, "floor": None}


@pytest.mark.asyncio
async def test_get_room_availability_uncorrect_date(
    client: AsyncClient,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    response = await room_api.get_availability(
        auth_data_user,
        room_id=1,
        date="2026-06-01",
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Date in the past"


@pytest.mark.asyncio
async def test_update_room(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.update(
        auth_data_user,
        room_id=room.id,
        title="Test Room 1 (Rename)",
    )
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_delete_room_user(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    room_api = RoomAPI(client)

    room = await RoomFactory.create(db_session)

    response = await room_api.delete(auth_data_user, room_id=room.id)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_delete_room(client: AsyncClient, db_session: AsyncSession):
    user = await UserFactory.create(db_session, role=UserRole.ADMIN)

    auth = AuthAPI(client)
    room_api = RoomAPI(client)
    booking_api = BookingAPI(client)

    response = await auth.login()
    auth_data = response.json()

    room = await RoomFactory.create(db_session)

    await SlotFactory.create(db_session, room_id=room.id)

    msc_datetime = BaseFactory._get_msc_datetime()

    response = await room_api.get_availability(auth_data, room_id=room.id)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "slots": [
            {
                "start_time": "08:00:00",
                "end_time": "12:00:00",
            }
        ]
    }

    response = await booking_api.create(auth_data, room.id)
    data = response.json()
    booking_id = data["id"]

    booking_start_time = BaseFactory._response_strftime_time(
        msc_datetime.replace(
            hour=8,
            minute=0,
            second=0,
        )
    )
    booking_end_time = BaseFactory._response_strftime_time(
        msc_datetime.replace(
            hour=8,
            minute=10,
            second=0,
        )
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert data == {
        "id": booking_id,
        "user_id": user.id,
        "room_id": room.id,
        "start_time": booking_start_time,
        "end_time": booking_end_time,
        "description": "Test Description",
    }

    response = await booking_api.get_multi(auth_data, room_id=room.id)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "bookings": [
            {
                "id": booking_id,
                "user_id": user.id,
                "room_id": room.id,
                "start_time": booking_start_time,
                "end_time": booking_end_time,
                "description": "Test Description",
            }
        ]
    }

    response = await room_api.delete(auth_data, room.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await room_api.get_availability(auth_data, room.id)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room is not found"

    response = await booking_api.get_multi(auth_data, room_id=room.id)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room is not found"
