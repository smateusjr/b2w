class BaseExceptionError(Exception):

    def __init__(self, error, description=None):
        self.error = error
        self.description = description
