from datetime import date

import pytest

from src.core.exceptions.room import RoomNotFoundException
from src.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from src.schemas.slot import SlotAvailability

from ..factories.booking import BookingFactory
from ..factories.room import RoomFactory
from ..factories.slot import SlotFactory


@pytest.mark.asyncio
async def test_create_room_success(room_repo, room_service):
    room = RoomFactory.build()

    room_repo.create.return_value = room

    result = await room_service.create_room(
        RoomCreate(
            title=room.title,
            floor=room.floor,
        )
    )

    assert result == RoomResponse.model_validate(room)

    room_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_rooms_success(room_repo, room_service):
    room = RoomFactory.build()

    room_repo.get_multi.return_value = [room]
    room_repo.count.return_value = 1

    offset = 0
    limit = 10
    floor = None
    result = await room_service.get_rooms(offset=offset, limit=limit, floor=floor)

    assert result == ([RoomResponse.model_validate(room)], 1)

    room_repo.get_multi.assert_called_once_with(offset, limit, floor)
    room_repo.count.assert_called_once()


@pytest.mark.asyncio
async def test_get_room_availability_success(
    room_repo,
    slot_repo,
    booking_repo,
    room_service,
):
    room = RoomFactory.build()
    slot = SlotFactory.build()

    date_in = date.today()
    slots_availability = room_service._get_slots_availability(
        date_in,
        slots=[slot],
        bookings=[],
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_multi.return_value = [slot]
    booking_repo.get_multi.return_value = []

    result = await room_service.get_room_availability(room.id, date_in=date_in)

    assert result == [SlotAvailability(**slot) for slot in slots_availability]

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_multi.assert_called_once_with(room.id)
    booking_repo.get_multi.assert_called_once_with(
        room.id,
        user_id=None,
        date_in=date_in,
    )


@pytest.mark.asyncio
async def test_get_room_availability_after_filling_booking_success(
    room_repo,
    slot_repo,
    booking_repo,
    room_service,
):
    room = RoomFactory.build()
    slot = SlotFactory.build()
    booking = BookingFactory.build()

    date_in = date.today()
    slots_availability = room_service._get_slots_availability(
        date_in,
        slots=[slot],
        bookings=[booking],
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_multi.return_value = [slot]
    booking_repo.get_multi.return_value = [booking]

    result = await room_service.get_room_availability(room.id, date_in)

    assert result == [SlotAvailability(**slot) for slot in slots_availability]

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_multi.assert_called_once_with(room.id)
    booking_repo.get_multi.assert_called_once_with(
        room.id,
        user_id=None,
        date_in=date_in,
    )


@pytest.mark.asyncio
async def test_get_room_by_id_success(room_repo, room_service):
    room = RoomFactory.build()

    room_repo.get_by_id.return_value = room

    result = await room_service.get_room_by_id(room.id)

    assert result == RoomResponse.model_validate(room)

    room_repo.get_by_id.assert_called_once_with(room.id)


@pytest.mark.asyncio
async def test_get_room_by_id_not_found(room_repo, room_service):
    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await room_service.get_room_by_id(room_id=1)

    room_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_update_room_success(room_repo, room_service):
    room = RoomFactory.build()
    update_room = RoomFactory.build(floor=2)

    room_repo.get_by_id.return_value = room
    room_repo.update.return_value = update_room

    result = await room_service.update_room(
        room.id,
        RoomUpdate(title="Room title", floor=2),
    )

    assert result == RoomResponse.model_validate(update_room)

    room_repo.get_by_id.assert_called_once_with(room.id)
    room_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_room_not_found(room_repo, room_service):
    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await room_service.update_room(
            room_id=1,
            room_in=RoomUpdate(title="Room title", floor=2),
        )

    room_repo.get_by_id.assert_called_once_with(1)
    room_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_room_success(room_repo, room_service):
    room = RoomFactory.build()

    room_repo.get_by_id.return_value = room
    room_repo.delete.return_value = None

    result = await room_service.delete_room(room.id)

    assert result is None

    room_repo.get_by_id.assert_called_once_with(room.id)
    room_repo.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_room_not_found(room_repo, room_service):
    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await room_service.delete_room(room_id=1)

    room_repo.get_by_id.assert_called_once_with(1)
    room_repo.delete.assert_not_called()
