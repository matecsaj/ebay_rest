# Standard library imports
import json


class Error(Exception):
    """
    Custom exception class for all errors raised by this library.

    This class encapsulates errors with unique error numbers, detailed messages,
    and optional contextual information, ensuring consistent exception handling
    and backward compatibility.

    Attributes:
        number: A unique natural number code identifying the error.
        reason: A short description of the error's cause.
        detail: Additional details about the error, if available.
        __cause__ : The original exception causing this error, if applicable.

    Usage Notes for Library Users:
        - Handle exceptions based on the `number` attribute for precise error handling.
        - Error numbers are stable and unlikely to change.
        - Use the `detail` attribute and original exception (`__cause__`) for debugging.

    Usage Notes for Library Maintainers:
        - Assign error numbers following the format of a two-digit prefix (module identifier)
          and a three-digit suffix (error identifier). Example: `96024`.
        - Avoid repurposing existing error numbers.
        - Preserve the original exception trace when re-raising by passing it via the `cause` argument.
        - Maintain backward compatibility when modifying this class.

    Methods:
        as_dict: Returns a dictionary representation of the error for structured logging.
        log: Logs the error message to the provided logger instance.

    Example:
        try:
            external_function()
        except ExternalLibraryError as e:
            raise Error(
                number=12345,
                reason="Failed during external library call",
                detail="Ensure API credentials are valid.",
                cause=e
            )
    """

    __slots__ = "number", "reason", "detail", "__cause__"

    def __init__(
        self, number: int, reason: str, detail: str = None, cause: Exception = None
    ) -> None:
        """
        Instantiate a new Error object.

        :param number: A unique natural number code.
        :param reason: A short description of the reason for the error.
        :param detail: Additional details about the failure.
        :param cause: The original exception causing this error.

        :return:
        """
        super().__init__()
        self.number = number
        self.reason = reason

        # try to tidy the detail if it is a JSON string or bytes
        if detail:
            if isinstance(detail, bytes):
                try:
                    detail = detail.decode("utf-8")
                except UnicodeDecodeError:
                    pass
            if isinstance(detail, str):
                try:
                    data = json.loads(detail)
                    detail = json.dumps(data, indent=4)
                except (json.JSONDecodeError, TypeError):
                    pass
        self.detail = detail

        self.__cause__ = cause  # Store the original exception if provided

    def __str__(self) -> str:
        """
        Returns the error message as a string.

        :return:
        """
        message = f"Error number {self.number}.\nReason: {self.reason or ''}"
        if self.detail:
            message += f"\nDetail: {self.detail}"
        if self.__cause__:
            message += f"\nCause: {type(self.__cause__).__name__}: {self.__cause__}"
        return message

    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the error.

        :return: A dictionary with the error's attributes.
        """
        return {
            "number": self.number,
            "reason": self.reason,
            "detail": self.detail,
            "cause": str(self.__cause__) if self.__cause__ else None,
        }

    def log(self, logger) -> None:
        """
        Logs the error message using the provided logger instance.

        :param logger: A logger instance with an `error` method.

        :return:
        """
        logger.error(self.__str__())
