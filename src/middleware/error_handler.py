import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions.base import MyBaseException
from src.core.exceptions.booking import (
    BookingException,
    BookingNotAvailableException,
    BookingNotFoundException,
)
from src.core.exceptions.common import (
    CrossDayBookingException,
    DateInPastException,
    InvalidTimeRangeException,
    TimeInvalidIncrementException,
    TimeTooShortException,
)
from src.core.exceptions.room import RoomException, RoomNotFoundException
from src.core.exceptions.slot import (
    BookingsOutsideNewSlotException,
    SlotException,
    SlotNotAvailableException,
    SlotNotFoundException,
)
from src.core.exceptions.user import (
    ForbiddenException,
    UserException,
    UserNotFoundException,
)

logger = structlog.get_logger()


def room_exception_handler(exc: RoomException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    detail = str(exc)

    if isinstance(exc, RoomNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Room is not found"

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


def slot_exception_handler(exc: SlotException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    detail = str(exc)

    if isinstance(exc, SlotNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Slot is not found"

    elif isinstance(exc, SlotNotAvailableException):
        detail = "Slot is not available"

    elif isinstance(exc, BookingsOutsideNewSlotException):
        detail = "Bookings would be outside new slot range"

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


def booking_exception_handler(exc: BookingException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    detail = str(exc)

    if isinstance(exc, BookingNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Booking is not found"
    elif isinstance(exc, BookingNotAvailableException):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Booking is not available"

    return JSONResponse(status_code=status_code, content={"detail": detail})


def user_exception_handler(exc: UserException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    detail = str(exc)

    if isinstance(exc, UserNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "User is not found"
    elif isinstance(exc, ForbiddenException):
        status_code = status.HTTP_403_FORBIDDEN
        detail = str(exc.args[0])

    return JSONResponse(status_code=status_code, content={"detail": detail})


async def my_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    detail = str(exc)

    if isinstance(exc, MyBaseException):
        if isinstance(exc, RoomException):
            return room_exception_handler(exc)
        elif isinstance(exc, SlotException):
            return slot_exception_handler(exc)
        elif isinstance(exc, BookingException):
            return booking_exception_handler(exc)
        elif isinstance(exc, UserException):
            return user_exception_handler(exc)

        elif isinstance(exc, InvalidTimeRangeException):
            detail = "Start time must be before end time"

        elif isinstance(exc, CrossDayBookingException):
            detail = "Booking must be within the same day"

        elif isinstance(exc, TimeTooShortException):
            detail = "Time must be at least 5 minutes long"

        elif isinstance(exc, TimeInvalidIncrementException):
            detail = "Time must be in 5 minutes increments"

        elif isinstance(exc, DateInPastException):
            detail = "Date in the past"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": detail},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, SQLAlchemyError):
        logger.error("database_error", error=str(exc))
    else:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
