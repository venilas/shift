from datetime import timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .api.booking import BookingAPI
from .factories.base import BaseFactory
from .factories.booking import BookingFactory
from .factories.room import RoomFactory
from .factories.slot import SlotFactory


@pytest.mark.asyncio
async def test_create_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await booking_api.create(auth_data_user, room.id)
    data = response.json()
    msc_datetime = BaseFactory._get_msc_datetime()

    assert data == {
        "id": data["id"],
        "room_id": room.id,
        "start_time": BaseFactory._response_strftime_time(
            msc_datetime.replace(
                hour=8,
                minute=0,
                second=0,
            )
        ),
        "end_time": BaseFactory._response_strftime_time(
            msc_datetime.replace(
                hour=8,
                minute=10,
                second=0,
            )
        ),
        "description": "Test Description",
    }
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_get_bookings_admin(client: AsyncClient, auth_data_admin: dict):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi(auth_data_admin)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {"bookings": []}


@pytest.mark.asyncio
async def test_get_bookings_admin_after_filling(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi(auth_data_admin)
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


@pytest.mark.asyncio
async def test_get_room_bookings_admin_after_filling(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi(auth_data_admin, room.id)
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


@pytest.mark.asyncio
async def test_get_user_bookings_admin_after_filling(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi(auth_data_admin, user_id=user_id)
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


@pytest.mark.asyncio
async def test_get_date_bookings_admin_after_filling(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi(
        auth_data_admin,
        date_in=BaseFactory._get_msc_datetime().date(),
    )
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


@pytest.mark.asyncio
async def test_update_booking_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    new_start_time = msc_datetime.replace(hour=8, minute=15, second=0)
    new_end_time = msc_datetime.replace(hour=8, minute=30, second=0)

    response = await booking_api.update(
        auth_data_admin,
        booking.id,
        start_time=new_start_time,
        end_time=new_end_time,
        description="Test Description (Rename)",
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "id": booking.id,
        "user_id": user_id,
        "room_id": room.id,
        "start_time": BaseFactory._response_strftime_time(new_start_time),
        "end_time": BaseFactory._response_strftime_time(new_end_time),
        "description": "Test Description (Rename)",
    }


@pytest.mark.asyncio
async def test_delete_booking_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.delete(auth_data_admin, booking.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi_user(auth_data_user)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "bookings": [
            {
                "id": booking.id,
                "room_id": room.id,
                "start_time": BaseFactory._response_strftime_time(booking.start_time),
                "end_time": BaseFactory._response_strftime_time(booking.end_time),
                "description": "Test Description",
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_room_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.get_multi_user(auth_data_user, room.id)

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "bookings": [
            {
                "id": booking.id,
                "room_id": room.id,
                "start_time": BaseFactory._response_strftime_time(booking.start_time),
                "end_time": BaseFactory._response_strftime_time(booking.end_time),
                "description": "Test Description",
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    new_end_time = msc_datetime.replace(hour=9, minute=10, second=0)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        end_time=new_end_time,
        description="Test Description (Rename)",
    )
    data = response.json()

    assert data == {
        "id": booking.id,
        "room_id": room.id,
        "start_time": BaseFactory._response_strftime_time(booking.start_time),
        "end_time": BaseFactory._response_strftime_time(new_end_time),
        "description": "Test Description (Rename)",
    }
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.delete_user(auth_data_user, booking.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_bookings_admin_invalid_user(
    client: AsyncClient,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi(auth_data_admin, user_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_bookings_admin_invalid_room(
    client: AsyncClient,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi(auth_data_admin, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_delete_booking_admin_invalid_booking(
    client: AsyncClient,
    auth_data_admin: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.delete(auth_data_admin, booking_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Booking not found"


@pytest.mark.asyncio
async def test_create_booking_unauthorize(client: AsyncClient):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi_user(auth_data={})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_booking_short_description(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await booking_api.create(auth_data_user, room.id, description="")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 1 character"


@pytest.mark.asyncio
async def test_create_booking_long_description(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await booking_api.create(auth_data_user, room.id, description="T" * 201)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 200 characters"


@pytest.mark.asyncio
async def test_create_booking_invalid_room(
    client: AsyncClient,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.create(auth_data_user, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_create_booking_slot_not_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    start_time = msc_datetime.replace(hour=10, minute=0, second=0)
    end_time = msc_datetime.replace(hour=13, minute=0, second=0)

    response = await booking_api.create(auth_data_user, room.id, start_time, end_time)

    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Booking must be inside room slot"


@pytest.mark.asyncio
async def test_create_booking_not_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()

    await booking_api.create(
        auth_data_user,
        room.id,
        end_time=msc_datetime.replace(hour=8, minute=30, second=0),
    )
    response = await booking_api.create(
        auth_data_user,
        room.id,
        start_time=msc_datetime.replace(hour=8, minute=15, second=0),
        end_time=msc_datetime.replace(hour=8, minute=45, second=0),
    )
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Booking overlaps with another booking"


@pytest.mark.asyncio
async def test_create_booking_different_date(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    start_time = msc_datetime.replace(hour=8, minute=0, second=0)
    end_time = start_time + timedelta(days=1, minutes=10)

    response = await booking_api.create(auth_data_user, room.id, start_time, end_time)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Booking must be within the same day"


@pytest.mark.asyncio
async def test_create_booking_start_time_must_end_time(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    start_time = msc_datetime.replace(hour=8, minute=10, second=0)
    end_time = msc_datetime.replace(hour=8, minute=0, second=0)

    response = await booking_api.create(auth_data_user, room.id, start_time, end_time)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Start time must be before end time"


@pytest.mark.asyncio
async def test_create_booking_5_minutes_increments(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    end_time = msc_datetime.replace(hour=8, minute=13, second=0)

    response = await booking_api.create(auth_data_user, room.id, end_time=end_time)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be in 5 minutes increments"


@pytest.mark.asyncio
async def test_create_booking_least_5_minutes(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    end_time = msc_datetime.replace(hour=8, minute=3, second=0)
    response = await booking_api.create(auth_data_user, room.id, end_time=end_time)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be at least 5 minutes long"


@pytest.mark.asyncio
async def test_get_bookings_invalid_room(
    client: AsyncClient,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi_user(auth_data_user, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_get_bookings_not_admin(client: AsyncClient, auth_data_user: dict):
    booking_api = BookingAPI(client)

    response = await booking_api.get_multi(auth_data_user)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_update_alien_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    admin_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    booking = await BookingFactory.create(db_session, admin_id, room.id)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        description="Test Description (Rename)",
    )
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Not permission to update this booking"


@pytest.mark.asyncio
async def test_update_booking_invalid_room(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.update_user(auth_data_user, booking.id, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_update_booking_not_slot_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    start_time = msc_datetime.replace(hour=7, minute=0, second=0)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        start_time=start_time,
    )
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Booking must be inside room slot"


@pytest.mark.asyncio
async def test_update_booking_not_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    await BookingFactory.create(db_session, user_id, room.id)

    msc_datetime = BaseFactory._get_msc_datetime()
    start_time = msc_datetime.replace(hour=8, minute=10, second=0)
    end_time = msc_datetime.replace(hour=8, minute=20, second=0)
    booking = await BookingFactory.create(
        db_session,
        user_id,
        room.id,
        start_time,
        end_time,
    )

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        start_time=start_time.replace(minute=5),
    )
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Booking overlaps with another booking"


@pytest.mark.asyncio
async def test_update_booking_different_date(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        end_time=booking.end_time + timedelta(days=1),
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Booking must be within the same day"


@pytest.mark.asyncio
async def test_update_booking_start_time_must_end_time(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        start_time=booking.start_time.replace(minute=20),
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Start time must be before end time"


@pytest.mark.asyncio
async def test_update_booking_5_minutes_increments(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        end_time=booking.end_time.replace(minute=13),
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be in 5 minutes increments"


@pytest.mark.asyncio
async def test_update_booking_least_5_minutes(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_user)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, user_id, room.id)

    response = await booking_api.update_user(
        auth_data_user,
        booking.id,
        start_time=booking.start_time.replace(minute=7),
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be at least 5 minutes long"


@pytest.mark.asyncio
async def test_delete_alien_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)
    admin_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    booking = await BookingFactory.create(db_session, admin_id, room.id)

    response = await booking_api.delete_user(auth_data_user, booking.id)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Not permission to delete this booking"


@pytest.mark.asyncio
async def test_delete_booking_invalid_room(
    client: AsyncClient,
    auth_data_user: dict,
):
    booking_api = BookingAPI(client)

    response = await booking_api.delete_user(auth_data_user, booking_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Booking not found"
