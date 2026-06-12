from .base import MyBaseException


class BookingException(MyBaseException):
    pass


class BookingNotFoundException(BookingException):
    pass


class BookingNotAvailableException(BookingException):
    pass
