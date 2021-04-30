

class Error(Exception):
    """ Used to return all exceptions from this module. """

    def __init__(self, number, message):
        super().__init__()
        self.number = number
        self.message = message

    def __str__(self):
        return f'Error {self.number} is {self.message}.'
