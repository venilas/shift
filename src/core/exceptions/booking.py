from .base import MyBaseException


class BookingException(MyBaseException):
    pass


class BookingNotFoundException(BookingException):
    pass


class BookingOverlapException(BookingException):
    pass


class BookingOutsideSlotException(BookingException):
    pass
