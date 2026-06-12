class MyBaseException(Exception):
    def __init__(self, message=None, *args):
        super().__init__(message, *args)
