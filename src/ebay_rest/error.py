class Error(Exception):
    """
    Custom exception class for all errors raised by this library.

    This class encapsulates errors with unique error numbers, detailed messages,
    and optional contextual information, ensuring consistent exception handling
    and backward compatibility.

    Attributes:
        number (int): A unique natural number code identifying the error.
        reason (str): A short description of the error's cause.
        detail (str, optional): Additional details about the error, if available.
        __cause__ (Exception, optional): The original exception causing this error,
                                         if applicable.

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

        Args:
            number (int): A unique natural number code.
            reason (str): A short description of the reason for the error.
            detail (str, optional): Additional details about the failure.
            cause (Exception, optional): The original exception causing this error.

        Returns:
            None
        """
        super().__init__()
        self.number = number
        self.reason = reason
        self.detail = detail
        self.__cause__ = cause  # Store the original exception if provided

    def __str__(self) -> str:
        """
        Returns the error message as a string.

        Returns:
            str: A formatted error message including the number, reason, detail,
                 and cause (if applicable).
        """
        message = f"Error number {self.number}. {self.reason or ''} {self.detail or ''}".strip()
        if self.__cause__:
            message += f" (caused by {type(self.__cause__).__name__}: {self.__cause__})"
        return message

    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the error.

        Returns:
            dict: A dictionary with the error's attributes.
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

        Args:
            logger: A logger instance with a `error` method.

        Returns:
            None
        """
        logger.error(self.__str__())
