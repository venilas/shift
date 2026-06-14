from datetime import time

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .api.slot import SlotAPI
from .factories.base import BaseFactory
from .factories.booking import BookingFactory
from .factories.room import RoomFactory
from .factories.slot import SlotFactory


@pytest.mark.asyncio
async def test_create_slot_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)

    response = await slot_api.create(auth_data_admin, room.id)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data == {
        "id": data["id"],
        "room_id": room.id,
        "start_time": "08:00:00",
        "end_time": "12:00:00",
    }


@pytest.mark.asyncio
async def test_get_slots(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.get(auth_data_admin, room.id)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "slots": [
            {
                "id": slot.id,
                "room_id": room.id,
                "start_time": "08:00:00",
                "end_time": "12:00:00",
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_slot_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    await RoomFactory.create(db_session)
    room = await RoomFactory.create(db_session, title="Test Room 2", floor=2)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.update(
        auth_data_admin,
        slot.id,
        room.id,
        end_time="13:00",
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "id": slot.id,
        "room_id": room.id,
        "start_time": "08:00:00",
        "end_time": "13:00:00",
    }


@pytest.mark.asyncio
async def test_delete_slot_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.delete(auth_data_admin, slot.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_create_slot_admin_invalid_room_id(
    client: AsyncClient,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    response = await slot_api.create(auth_data_admin, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_create_slot_admin_not_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await slot_api.create(auth_data_admin, room.id, "09:00", "11:00")
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Slot overlaps with another slot"


@pytest.mark.asyncio
async def test_create_slot_admin_invalid_time(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)

    response = await slot_api.create(auth_data_admin, room.id, start_time="90:00")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        data["detail"][0]["msg"]
        == "Input should be in a valid time format, hour value is outside expected range of 0-23"
    )


@pytest.mark.asyncio
async def test_create_slot_admin_invalid_start_time_greater_end_time(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)

    response = await slot_api.create(
        auth_data_admin,
        room.id,
        start_time="12:00",
        end_time="08:00",
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Start time must be before end time"


@pytest.mark.asyncio
async def test_create_slot_5_minutes_increments(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)

    response = await slot_api.create(
        auth_data_admin,
        room.id,
        end_time="11:59",
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be in 5 minutes increments"


@pytest.mark.asyncio
async def test_create_slot_least_5_minutes(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)

    response = await slot_api.create(
        auth_data_admin,
        room.id,
        end_time="08:03",
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be at least 5 minutes long"


@pytest.mark.asyncio
async def test_get_slots_invalid_room(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await slot_api.get(auth_data_admin, room_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_get_slots_not_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_user: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)

    response = await slot_api.get(auth_data_user, room_id=room.id)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_update_slot_admin_invalid_slot_id(
    client: AsyncClient,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    response = await slot_api.update(
        auth_data_admin,
        slot_id=1_000,
        end_time="13:00",
    )
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Slot not found"


@pytest.mark.asyncio
async def test_update_slot_admin_invalid_room_id(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.update(
        auth_data_admin,
        slot.id,
        room_id=1_000,
        end_time="13:00",
    )
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_update_slot_admin_not_available(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    await SlotFactory.create(db_session, room.id)
    slot = await SlotFactory.create(
        db_session,
        room.id,
        start_time=time(14, 0),
        end_time=time(18, 0),
    )

    response = await slot_api.update(auth_data_admin, slot.id, start_time="11:00")
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Slot overlaps with another slot"


@pytest.mark.asyncio
async def test_update_slot_booking_outside_new_slot(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)
    user_id = BaseFactory._get_user_id(auth_data_admin)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)
    msc_datetime = BaseFactory._get_msc_datetime()
    await BookingFactory.create(
        db_session,
        user_id,
        room.id,
        start_time=msc_datetime.replace(hour=10, minute=0, second=0),
        end_time=msc_datetime.replace(hour=11, minute=30, second=0),
    )

    response = await slot_api.update(auth_data_admin, slot.id, end_time="11:00")
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        data["detail"]
        == "Slot cannot be updated because existing bookings would be outside new range"
    )


@pytest.mark.asyncio
async def test_update_slot_5_minutes_increments(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.update(auth_data_admin, slot.id, end_time="11:59")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be in 5 minutes increments"


@pytest.mark.asyncio
async def test_update_slot_least_5_minutes(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    room = await RoomFactory.create(db_session)
    slot = await SlotFactory.create(db_session, room.id)

    response = await slot_api.update(auth_data_admin, slot.id, end_time="08:03")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "Time must be at least 5 minutes long"


@pytest.mark.asyncio
async def test_delete_slot_admin_invalid_slot_id(
    client: AsyncClient,
    auth_data_admin: dict,
):
    slot_api = SlotAPI(client)

    response = await slot_api.delete(auth_data_admin, slot_id=1_000)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Slot not found"


@pytest.mark.asyncio
async def test_create_slot(client: AsyncClient, auth_data_user: dict):
    slot_api = SlotAPI(client)

    response = await slot_api.create(auth_data_user, room_id=1)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_update_slot(client: AsyncClient, auth_data_user: dict):
    slot_api = SlotAPI(client)

    response = await slot_api.update(auth_data_user, slot_id=1, end_time="13:00")
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_delete_slot(client: AsyncClient, auth_data_user: dict):
    slot_api = SlotAPI(client)

    response = await slot_api.delete(auth_data_user, slot_id=1)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "Forbidden"
