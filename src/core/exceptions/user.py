from .base import MyBaseException


class UserException(MyBaseException):
    pass


class UserNotFoundException(UserException):
    pass


class ForbiddenException(UserException):
    def __init__(self, message=None, *args):
        super().__init__(message, *args)


class InvalidTokenException(UserException):
    pass


class LoginAlreadyRegisteredException(UserException):
    pass


class IncorrectLoginOrPassword(UserException):
    pass
