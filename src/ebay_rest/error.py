

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

    __slots__ = "number", "reason", "detail"

    def __init__(self, number: int, reason: str, detail: str = None) -> None:
        """ Instantiate a new Error object.

        :param number (int, required) A unique natural number code.
        :param reason (str, required) A short description of the reason.
        :param detail (str, optional) The details about the failure, optional.
        :return None (None)
        """
        super().__init__()
        self.number = number
        self.reason = reason
        self.detail = detail

    def __str__(self) -> str:
        """
        :return message (str)
        """
        message = 'Error number' + str(self.number) + '.'
        if self.reason:
            message = message + ' ' + self.reason
        if self.detail:
            message = message + ' ' + self.detail
        return message
