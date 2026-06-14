from datetime import time

import pytest

from src.core.exceptions.room import RoomNotFoundException
from src.core.exceptions.slot import (
    SlotContainsBookingsException,
    SlotNotFoundException,
    SlotOverlapException,
)
from src.schemas.slot import SlotCreate, SlotResponse, SlotUpdate

from ..factories.room import RoomFactory
from ..factories.slot import SlotFactory


@pytest.mark.asyncio
async def test_create_slot_success(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.is_slot_available.return_value = True
    slot_repo.create.return_value = slot

    result = await slot_service.create_slot(
        SlotCreate(
            room_id=room.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
        )
    )

    assert result == SlotResponse.model_validate(slot)

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.is_slot_available.assert_called_once_with(
        room.id,
        slot.start_time,
        slot.end_time,
    )
    slot_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_slot_room_not_found(room_repo, slot_repo, slot_service):
    slot = SlotFactory.build()

    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await slot_service.create_slot(
            SlotCreate(
                room_id=1,
                start_time=slot.start_time,
                end_time=slot.end_time,
            )
        )

    room_repo.get_by_id.assert_called_once_with(1)
    slot_repo.is_slot_available.assert_not_called()
    slot_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_slot_overlap(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.is_slot_available.return_value = False

    with pytest.raises(SlotOverlapException):
        await slot_service.create_slot(
            SlotCreate(
                room_id=room.id,
                start_time=slot.start_time,
                end_time=slot.end_time,
            )
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.is_slot_available.assert_called_once_with(
        room.id,
        slot.start_time,
        slot.end_time,
    )
    slot_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_slots_success(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.get_multi.return_value = [slot]

    result = await slot_service.get_slots(room.id)

    assert result == [SlotResponse.model_validate(slot)]

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_multi.assert_called_once_with(room.id)


@pytest.mark.asyncio
async def test_get_slots_room_not_found(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()

    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await slot_service.get_slots(room.id)

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_multi.assert_not_called()


@pytest.mark.asyncio
async def test_update_slot_success(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()
    update_slot = SlotFactory.build(
        start_time=time(hour=7),
        end_time=time(hour=13),
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_by_id.return_value = slot
    slot_repo.is_slot_available.return_value = True
    slot_repo.is_bookings_available.return_value = True
    slot_repo.update.return_value = update_slot

    result = await slot_service.update_slot(
        slot.id,
        SlotUpdate(
            room_id=room.id,
            start_time=update_slot.start_time,
            end_time=update_slot.end_time,
        ),
    )

    assert result == SlotResponse.model_validate(update_slot)

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_by_id.assert_called_once_with(slot.id)
    slot_repo.is_slot_available.assert_called_once_with(
        update_slot.room_id,
        update_slot.start_time,
        update_slot.end_time,
        without_slot_id=slot.id,
    )
    slot_repo.is_bookings_available.assert_called_once_with(
        update_slot.room_id,
        update_slot.start_time,
        update_slot.end_time,
    )
    slot_repo.update.assert_called_once_with(
        slot.id,
        {
            "room_id": room.id,
            "start_time": update_slot.start_time,
            "end_time": update_slot.end_time,
        },
    )


@pytest.mark.asyncio
async def test_update_slot_contains_bookings(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()
    update_slot = SlotFactory.build(
        start_time=time(hour=7),
        end_time=time(hour=13),
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_by_id.return_value = slot
    slot_repo.is_slot_available.return_value = True
    slot_repo.is_bookings_available.return_value = False

    with pytest.raises(SlotContainsBookingsException):
        await slot_service.update_slot(
            slot.id,
            SlotUpdate(
                room_id=room.id,
                start_time=update_slot.start_time,
                end_time=update_slot.end_time,
            ),
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_by_id.assert_called_once_with(slot.id)
    slot_repo.is_slot_available.assert_called_once_with(
        update_slot.room_id,
        update_slot.start_time,
        update_slot.end_time,
        without_slot_id=slot.id,
    )
    slot_repo.is_bookings_available.assert_called_once_with(
        update_slot.room_id,
        update_slot.start_time,
        update_slot.end_time,
    )
    slot_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_slot_overlap(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    slot = SlotFactory.build()
    update_slot = SlotFactory.build(
        start_time=time(hour=7),
        end_time=time(hour=13),
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_by_id.return_value = slot
    slot_repo.is_slot_available.return_value = False

    with pytest.raises(SlotOverlapException):
        await slot_service.update_slot(
            slot.id,
            SlotUpdate(
                room_id=room.id,
                start_time=update_slot.start_time,
                end_time=update_slot.end_time,
            ),
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_by_id.assert_called_once_with(slot.id)
    slot_repo.is_slot_available.assert_called_once_with(
        update_slot.room_id,
        update_slot.start_time,
        update_slot.end_time,
        without_slot_id=slot.id,
    )
    slot_repo.is_bookings_available.assert_not_called()
    slot_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_slot_not_found(room_repo, slot_repo, slot_service):
    room = RoomFactory.build()
    update_slot = SlotFactory.build(
        start_time=time(hour=7),
        end_time=time(hour=13),
    )

    room_repo.get_by_id.return_value = room
    slot_repo.get_by_id.return_value = None

    with pytest.raises(SlotNotFoundException):
        await slot_service.update_slot(
            slot_id=1,
            slot_in=SlotUpdate(
                room_id=room.id,
                start_time=update_slot.start_time,
                end_time=update_slot.end_time,
            ),
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.get_by_id.assert_called_once_with(1)
    slot_repo.is_slot_available.assert_not_called()
    slot_repo.is_bookings_available.assert_not_called()
    slot_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_slot_room_not_found(room_repo, slot_repo, slot_service):
    update_slot = SlotFactory.build(
        start_time=time(hour=7),
        end_time=time(hour=13),
    )

    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await slot_service.update_slot(
            slot_id=1,
            slot_in=SlotUpdate(
                room_id=1,
                start_time=update_slot.start_time,
                end_time=update_slot.end_time,
            ),
        )

    room_repo.get_by_id.assert_called_once_with(1)
    slot_repo.get_by_id.assert_not_called()
    slot_repo.is_slot_available.assert_not_called()
    slot_repo.is_bookings_available.assert_not_called()
    slot_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_slot_success(slot_repo, slot_service):
    slot = SlotFactory.build()

    slot_repo.get_by_id.return_value = slot
    slot_repo.delete.return_value = None

    result = await slot_service.delete_slot(slot.id)

    assert result is None

    slot_repo.get_by_id.assert_called_once_with(slot.id)
    slot_repo.delete.assert_called_once_with(slot.id)


@pytest.mark.asyncio
async def test_delete_slot_not_found(slot_repo, slot_service):
    slot_repo.get_by_id.return_value = None

    with pytest.raises(SlotNotFoundException):
        await slot_service.delete_slot(1)

    slot_repo.get_by_id.assert_called_once_with(1)
    slot_repo.delete.assert_not_called()
