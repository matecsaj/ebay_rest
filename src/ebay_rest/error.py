

class Error(Exception):
    """ Used to return all exceptions from this package.

    End user notes:
    When writing exception-handling code, take action based on the error number.
    Error numbers are unlikely to change, but the descriptive text will evolve.

    Library maintainer notes.
    The error number is composed of a two-digit prefix and a three-digit suffix.
    Each new internal module is assigned a unique prefix counting down from 99.
    Give new "raises" within a module a unique suffix counting up from 001.
    Refrain from repurposing error numbers.
    Refrain from altering the error number or text descriptions when re-raising.
    """

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
        message = 'Error number' + str(self.number) + '.'
        if self.reason:
            message = message + ' ' + self.reason
        if self.detail:
            message = message + ' ' + self.detail
        return message
