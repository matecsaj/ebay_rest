# Standard library imports

# Third party imports

# Local imports

# Globals

class _Error(Exception):
    """An abstract base class for exceptions in this module."""
    pass


class EbayRestError(_Error):

    def __init__(self, number, message):
        self.number = number
        self.message = message

    def __str__(self):
        return f'Error {self.number} is {self.message}.'


class _Singleton(object):
    """ An abstract base class used to make Singletons.
    The singleton software design pattern restricts the instantiation of a class to one "single" instance.
    This is useful when exactly one object is needed to coordinate actions across the system.
    """
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


# class EbayRest(_Singleton):    # TODO If init parameters repeat then use a singleton to conserve resources.
class EbayRest:
    """ """

    def __init__(self, my_string):
        self.my_string = my_string
        return

    def print(self):
        print(self.my_string)

    def will_fail(self):
        raise EbayRestError(0, "Sample error.")

    @staticmethod
    def true():
        return True
