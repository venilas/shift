from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.config.settings import get_settings
from src.core.exceptions.booking import (
    BookingNotFoundException,
    BookingOutsideSlotException,
    BookingOverlapException,
)
from src.core.exceptions.room import RoomNotFoundException
from src.core.exceptions.user import ForbiddenException, UserNotFoundException
from src.models.enums import UserRole
from src.schemas.booking import BookingCreate, BookingResponse, BookingUpdate

from ..factories.booking import BookingFactory
from ..factories.room import RoomFactory
from ..factories.user import UserFactory


@pytest.mark.asyncio
async def test_create_booking_success(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = True
    booking_repo.is_booking_available.return_value = True
    booking_repo.create.return_value = booking

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz)
    start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=5)

    result = await booking_service.create_booking(
        BookingCreate(
            room_id=room.id,
            start_time=start_time,
            end_time=end_time,
            description=booking.description,
        ),
        current_user=user,
    )

    assert result == BookingResponse.model_validate(booking)

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.is_booking_available.assert_called_once_with(
        room.id,
        start_time,
        end_time,
    )
    booking_repo.is_booking_available.assert_called_once_with(
        room.id,
        start_time,
        end_time,
    )
    booking_repo.create.assert_called_once_with(
        {
            "room_id": room.id,
            "start_time": start_time,
            "end_time": end_time,
            "description": booking.description,
            "user_id": user.id,
        }
    )


@pytest.mark.asyncio
async def test_create_booking_overlap(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = True
    booking_repo.is_booking_available.return_value = False

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz)
    start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=5)

    with pytest.raises(BookingOverlapException):
        await booking_service.create_booking(
            BookingCreate(
                room_id=room.id,
                start_time=start_time,
                end_time=end_time,
                description=booking.description,
            ),
            current_user=user,
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.is_booking_available.assert_called_once_with(
        room.id,
        start_time,
        end_time,
    )
    booking_repo.is_booking_available.assert_called_once_with(
        room.id,
        start_time,
        end_time,
    )
    booking_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_booking_outside_slot(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = False

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz)
    start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=5)

    with pytest.raises(BookingOutsideSlotException):
        await booking_service.create_booking(
            BookingCreate(
                room_id=room.id,
                start_time=start_time,
                end_time=end_time,
                description=booking.description,
            ),
            current_user=user,
        )

    room_repo.get_by_id.assert_called_once_with(room.id)
    slot_repo.is_booking_available.assert_called_once_with(
        room.id,
        start_time,
        end_time,
    )
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_booking_room_not_found(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    booking = BookingFactory.build()
    user = UserFactory.build()

    room_repo.get_by_id.return_value = None

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    today = datetime.now(tz=tz)
    start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=5)

    with pytest.raises(RoomNotFoundException):
        await booking_service.create_booking(
            BookingCreate(
                room_id=1,
                start_time=start_time,
                end_time=end_time,
                description=booking.description,
            ),
            current_user=user,
        )

    room_repo.get_by_id.assert_called_once_with(1)
    slot_repo.is_booking_available.assert_not_called()
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_bookings_success(
    room_repo,
    user_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    user = UserFactory.build()
    booking = BookingFactory.build()

    room_repo.get_by_id.return_value = room
    user_repo.get_by_id.return_value = user
    booking_repo.get_multi.return_value = [booking]

    result = await booking_service.get_bookings(room.id, user.id, date_in=None)

    assert result == [BookingResponse.model_validate(booking)]

    room_repo.get_by_id.assert_called_once_with(room.id)
    user_repo.get_by_id.assert_called_once_with(user.id)
    booking_repo.get_multi.assert_called_once_with(room.id, user.id, None)


@pytest.mark.asyncio
async def test_get_bookings_room_not_found(
    room_repo,
    user_repo,
    booking_repo,
    booking_service,
):
    user = UserFactory.build()

    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await booking_service.get_bookings(room_id=1, user_id=user.id, date_in=None)

    room_repo.get_by_id.assert_called_once_with(1)
    user_repo.get_by_id.assert_not_called()
    booking_repo.get_multi.assert_not_called()


@pytest.mark.asyncio
async def test_get_bookings_admin_user_not_found(
    room_repo,
    user_repo,
    booking_repo,
    booking_service,
):
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        await booking_service.get_bookings(room_id=None, user_id=1, date_in=None)

    user_repo.get_by_id.assert_called_once_with(1)
    room_repo.get_by_id.assert_not_called()
    booking_repo.get_multi.assert_not_called()


@pytest.mark.asyncio
async def test_update_booking_success(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = booking
    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = True
    booking_repo.is_booking_available.return_value = True
    booking_repo.update.return_value = update_booking

    result = await booking_service.update_booking(
        booking.id,
        BookingUpdate(
            room_id=update_booking.room_id,
            end_time=update_booking.end_time,
        ),
        user,
    )

    assert result == BookingResponse.model_validate(update_booking)

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_called_once_with(update_booking.room_id)
    slot_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
    )
    booking_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
        booking.id,
    )
    booking_repo.update.assert_called_once_with(
        booking.id,
        {
            "room_id": update_booking.room_id,
            "end_time": update_booking.end_time,
        },
    )


@pytest.mark.asyncio
async def test_update_booking_overlap(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = booking
    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = True
    booking_repo.is_booking_available.return_value = False

    with pytest.raises(BookingOverlapException):
        await booking_service.update_booking(
            booking.id,
            BookingUpdate(
                room_id=update_booking.room_id,
                end_time=update_booking.end_time,
            ),
            user,
        )

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_called_once_with(update_booking.room_id)
    slot_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
    )
    booking_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
        booking.id,
    )
    booking_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_booking_outside_slot(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build()

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = booking
    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = False

    with pytest.raises(BookingOutsideSlotException):
        await booking_service.update_booking(
            booking.id,
            BookingUpdate(
                room_id=update_booking.room_id,
                end_time=update_booking.end_time,
            ),
            user,
        )

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_called_once_with(update_booking.room_id)
    slot_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
    )
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_booking_room_not_found(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    booking = BookingFactory.build()
    user = UserFactory.build()

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = booking
    room_repo.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundException):
        await booking_service.update_booking(
            booking.id,
            BookingUpdate(
                room_id=update_booking.room_id,
                end_time=update_booking.end_time,
            ),
            user,
        )

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_called_once_with(update_booking.room_id)
    slot_repo.is_booking_available.assert_not_called()
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_booking_not_found(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    booking = BookingFactory.build()
    user = UserFactory.build()

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = None

    with pytest.raises(BookingNotFoundException):
        await booking_service.update_booking(
            booking.id,
            BookingUpdate(
                room_id=update_booking.room_id,
                end_time=update_booking.end_time,
            ),
            user,
        )

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_not_called()
    slot_repo.is_booking_available.assert_not_called()
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_alier_booking_admin(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):

    room = RoomFactory.build()
    booking = BookingFactory.build()
    user = UserFactory.build(id=2, role=UserRole.ADMIN)

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    booking_repo.get_by_id.return_value = booking
    room_repo.get_by_id.return_value = room
    slot_repo.is_booking_available.return_value = True
    booking_repo.is_booking_available.return_value = True
    booking_repo.update.return_value = update_booking

    result = await booking_service.update_booking(
        booking.id,
        BookingUpdate(
            room_id=update_booking.room_id,
            end_time=update_booking.end_time,
        ),
        user,
    )

    assert result == BookingResponse.model_validate(update_booking)

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_called_once_with(update_booking.room_id)
    slot_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
    )
    booking_repo.is_booking_available.assert_called_once_with(
        update_booking.room_id,
        booking.start_time,
        update_booking.end_time,
        booking.id,
    )
    booking_repo.update.assert_called_once_with(
        booking.id,
        {
            "room_id": update_booking.room_id,
            "end_time": update_booking.end_time,
        },
    )


@pytest.mark.asyncio
async def test_update_alier_booking_not_admin(
    room_repo,
    slot_repo,
    booking_repo,
    booking_service,
):
    booking = BookingFactory.build()
    user = UserFactory.build(id=2)

    tz = ZoneInfo(key=get_settings().TIMEZONE)
    end_time = booking.end_time.astimezone(tz=tz).replace(minute=10)
    update_booking = BookingFactory.build(room_id=2, end_time=end_time)

    with pytest.raises(ForbiddenException):
        await booking_service.update_booking(
            booking.id,
            BookingUpdate(
                room_id=update_booking.room_id,
                end_time=update_booking.end_time,
            ),
            user,
        )

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    room_repo.get_by_id.assert_not_called()
    slot_repo.is_booking_available.assert_not_called()
    booking_repo.is_booking_available.assert_not_called()
    booking_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_booking_success(booking_repo, booking_service):
    booking = BookingFactory.build()
    user = UserFactory.build()

    booking_repo.get_by_id.return_value = booking
    booking_repo.delete.return_value = None

    result = await booking_service.delete_booking(booking.id, user)

    assert result is None

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    booking_repo.delete.assert_called_once_with(booking.id)


@pytest.mark.asyncio
async def test_delete_booking_not_found(booking_repo, booking_service):
    user = UserFactory.build()

    booking_repo.get_by_id.return_value = None

    with pytest.raises(BookingNotFoundException):
        await booking_service.delete_booking(booking_id=1, current_user=user)

    booking_repo.get_by_id.assert_called_once_with(1)
    booking_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_alier_booking_admin(booking_repo, booking_service):
    booking = BookingFactory.build()
    user = UserFactory.build(id=2, role=UserRole.ADMIN)

    booking_repo.get_by_id.return_value = booking
    booking_repo.delete.return_value = None

    result = await booking_service.delete_booking(booking.id, user)

    assert result is None

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    booking_repo.delete.assert_called_once_with(booking.id)


@pytest.mark.asyncio
async def test_delete_alier_booking(booking_repo, booking_service):
    booking = BookingFactory.build()
    user = UserFactory.build(id=2)

    booking_repo.get_by_id.return_value = booking

    with pytest.raises(ForbiddenException):
        await booking_service.delete_booking(booking.id, user)

    booking_repo.get_by_id.assert_called_once_with(booking.id)
    booking_repo.delete.assert_not_called()
