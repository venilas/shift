from .base import MyBaseException


class RoomException(MyBaseException):
    pass


class RoomNotFoundException(RoomException):
    pass
