from .base import MyBaseException


class SlotException(MyBaseException):
    pass


class SlotNotFoundException(SlotException):
    pass


class SlotNotAvailableException(SlotException):
    pass


class BookingsOutsideNewSlotException(SlotException):
    pass
