from .base import MyBaseException


class InvalidTimeRangeException(MyBaseException):
    pass


class CrossDayBookingException(MyBaseException):
    pass


class TimeTooShortException(MyBaseException):
    pass


class TimeInvalidIncrementException(MyBaseException):
    pass


class DateInPastException(MyBaseException):
    pass
