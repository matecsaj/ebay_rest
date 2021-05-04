

class Error(Exception):
    """ Used to return all exceptions from this module. """

    def __init__(self, number: int, reason: str, detail: str = None):
        """ Instantiate a new Error object.

        :param int number: A unique natural number code.
        :param str reason: A short description of the reason.
        :param str detail: The details about the failure, optional.
        :rtype: object
        """
        super().__init__()
        self.number = number
        self.reason = reason
        self.detail = detail

    def __str__(self):
        return 'Error ' + str(self.number) + ' is ' + self.reason + ' with detail: ' + self.detail + '.'
