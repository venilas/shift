from .base import MyBaseException


class SlotException(MyBaseException):
    pass


class SlotNotFoundException(SlotException):
    pass


class SlotOverlapException(SlotException):
    pass


class SlotContainsBookingsException(SlotException):
    pass
